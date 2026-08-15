"""Recreate the questions table so it matches init_db().

Databases created before the schema fix are missing the CHECK constraint on
status (and, on the oldest databases, the status/sent_at columns themselves).
SQLite cannot add a CHECK with ALTER TABLE, so the table is rebuilt and the
rows copied across.

Safe to run more than once: it exits early when the constraint is present.
"""

import shutil
import sqlite3
from datetime import datetime, timezone

from tutor.db.database import DB_PATH


QUESTIONS_TABLE = """
    CREATE TABLE questions (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        question TEXT NOT NULL,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        reference_context TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'sent', 'answered')),
        sent_at TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (book_id) REFERENCES books(id)
    )
"""

VALID_STATUSES = ("pending", "sent", "answered")


def current_schema(connection: sqlite3.Connection) -> str | None:
    row = connection.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table' AND name = 'questions'
        """
    ).fetchone()

    return None if row is None else row[0]


def backup_database() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_path = DB_PATH.with_suffix(f".{stamp}.backup.db")

    shutil.copy2(DB_PATH, backup_path)

    return str(backup_path)


def migrate() -> None:
    if not DB_PATH.exists():
        print(f"Nothing to migrate: {DB_PATH} does not exist.")
        return

    connection = sqlite3.connect(DB_PATH)

    try:
        schema = current_schema(connection)

        if schema is None:
            print("Nothing to migrate: questions table does not exist.")
            return

        if "CHECK (status IN" in schema:
            print("Already migrated: status CHECK constraint is present.")
            return

        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(questions)")
        }

        # Oldest databases predate these columns entirely.
        has_status = "status" in columns
        has_sent_at = "sent_at" in columns

        if has_status:
            invalid = connection.execute(
                f"""
                SELECT DISTINCT status
                FROM questions
                WHERE status NOT IN ({','.join('?' * len(VALID_STATUSES))})
                """,
                VALID_STATUSES,
            ).fetchall()

            if invalid:
                values = ", ".join(repr(row[0]) for row in invalid)
                raise SystemExit(
                    "Aborting: questions contain status values that the new "
                    f"CHECK constraint would reject: {values}"
                )

        before = connection.execute(
            "SELECT count(*) FROM questions"
        ).fetchone()[0]

        backup_path = backup_database()
        print(f"Backup written to {backup_path}")

        status_source = "status" if has_status else "'pending'"
        sent_at_source = "sent_at" if has_sent_at else "NULL"

        # Foreign keys must be off while the table is swapped, otherwise the
        # answers -> questions references are rewritten to point at the
        # temporary table. This pragma is a no-op inside a transaction, so it
        # runs before one is opened.
        connection.execute("PRAGMA foreign_keys = OFF")

        try:
            connection.execute("BEGIN")

            connection.execute(
                QUESTIONS_TABLE.replace(
                    "CREATE TABLE questions",
                    "CREATE TABLE questions_migrated",
                )
            )

            connection.execute(
                f"""
                INSERT INTO questions_migrated (
                    id,
                    book_id,
                    question,
                    topic,
                    difficulty,
                    reference_context,
                    status,
                    sent_at,
                    created_at
                )
                SELECT
                    id,
                    book_id,
                    question,
                    topic,
                    difficulty,
                    reference_context,
                    {status_source},
                    {sent_at_source},
                    created_at
                FROM questions
                """
            )

            connection.execute("DROP TABLE questions")

            connection.execute(
                "ALTER TABLE questions_migrated RENAME TO questions"
            )

            after = connection.execute(
                "SELECT count(*) FROM questions"
            ).fetchone()[0]

            if after != before:
                raise RuntimeError(
                    f"Row count changed during migration: {before} -> {after}"
                )

            violations = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if violations:
                raise RuntimeError(
                    f"Foreign key violations after migration: {violations}"
                )

            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            print(
                "Migration rolled back; the database is unchanged. "
                f"A backup is still available at {backup_path}"
            )
            raise
        finally:
            connection.execute("PRAGMA foreign_keys = ON")

        print(f"Migrated {after} questions.")
    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
