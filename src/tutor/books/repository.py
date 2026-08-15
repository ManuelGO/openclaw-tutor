import json
from pathlib import Path
from uuid import uuid4

from tutor.books.models import Book
from tutor.db.database import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VECTOR_STORE_STATE = PROJECT_ROOT / "data" / "vector_store.json"


def save_book(book: Book) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO books (id, title, vector_store_id)
            VALUES (?, ?, ?)
            """,
            (
                book.id,
                book.title,
                book.vector_store_id,
            ),
        )


def get_book(book_id: str) -> Book | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, vector_store_id
            FROM books
            WHERE id = ?
            """,
            (book_id,),
        ).fetchone()

    if row is None:
        return None

    return Book(
        id=row["id"],
        title=row["title"],
        vector_store_id=row["vector_store_id"],
    )


def register_ingested_book(title: str = "Fluent Python") -> Book:
    """Register the book held in the saved vector store state.

    Bootstrap step for the ingestion flow: tutor.ingestion.ingest writes the
    vector store id, this links it to a title in the database.
    """
    existing = get_book_by_title(title)

    if existing is not None:
        return existing

    data = json.loads(VECTOR_STORE_STATE.read_text())

    book = Book(
        id=str(uuid4()),
        title=title,
        vector_store_id=data["vector_store_id"],
    )

    save_book(book)
    return book

def get_book_by_title(title: str) -> Book | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, vector_store_id
            FROM books
            WHERE title = ?
            """,
            (title,),
        ).fetchone()

    if row is None:
        return None

    return Book(
        id=row["id"],
        title=row["title"],
        vector_store_id=row["vector_store_id"],
    )


if __name__ == "__main__":
    import sys

    title = sys.argv[1] if len(sys.argv) > 1 else "Fluent Python"

    book = register_ingested_book(title)

    print("Book registered:")
    print(book)