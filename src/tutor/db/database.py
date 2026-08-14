from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "tutor.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                vector_store_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                book_id TEXT NOT NULL,
                question TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                reference_context TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            """
        )
        connection.execute(
        """
            CREATE TABLE IF NOT EXISTS answers (
                id TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                answer_id TEXT NOT NULL UNIQUE,
                score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
                feedback TEXT NOT NULL,
                strengths TEXT NOT NULL,
                gaps TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (answer_id) REFERENCES answers(id)
            )
            """
        )
        
if __name__ == "__main__":
    init_db()
    print(f"Database initialized: {DB_PATH}")