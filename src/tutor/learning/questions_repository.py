from tutor.db.database import get_connection
from tutor.learning.questions import Question


def save_question(question: Question) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO questions (
                id,
                book_id,
                question,
                topic,
                difficulty,
                reference_context
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                question.id,
                question.book_id,
                question.question,
                question.topic,
                question.difficulty,
                question.reference_context,
            ),
        )
        
def save_questions(questions: list[Question]) -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO questions (
                id,
                book_id,
                question,
                topic,
                difficulty,
                reference_context
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    question.id,
                    question.book_id,
                    question.question,
                    question.topic,
                    question.difficulty,
                    question.reference_context,
                )
                for question in questions
            ],
        )
        
def get_pending_questions(
    book_id: str,
    limit: int = 4,
) -> list[Question]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                book_id,
                question,
                topic,
                difficulty,
                reference_context
            FROM questions
            WHERE book_id = ?
              AND status = 'pending'
            ORDER BY created_at
            LIMIT ?
            """,
            (book_id, limit),
        ).fetchall()

    return [
        Question(
            id=row["id"],
            book_id=row["book_id"],
            question=row["question"],
            topic=row["topic"],
            difficulty=row["difficulty"],
            reference_context=row["reference_context"],
        )
        for row in rows
    ]
    
if __name__ == "__main__":
    from tutor.books.repository import get_book_by_title

    book = get_book_by_title("Fluent Python")

    if book is None:
        raise RuntimeError("Fluent Python is not registered")

    questions = get_pending_questions(
        book_id=book.id,
        limit=4,
    )

    for question in questions:
        print(f"[{question.difficulty}] {question.question}")
        print(f"ID: {question.id}")
        print()