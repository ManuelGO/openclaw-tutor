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
    
def get_question(question_id: str) -> Question | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                book_id,
                question,
                topic,
                difficulty,
                reference_context
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        ).fetchone()

    if row is None:
        return None

    return Question(
        id=row["id"],
        book_id=row["book_id"],
        question=row["question"],
        topic=row["topic"],
        difficulty=row["difficulty"],
        reference_context=row["reference_context"],
    )
    
def mark_question_answered(question_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE questions
            SET status = 'answered'
            WHERE id = ?
            """,
            (question_id,),
        )

def mark_question_sent(question_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE questions
            SET
                status = 'sent',
                sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (question_id,),
        )
        
def get_active_question(book_id: str) -> Question | None:
    with get_connection() as connection:
        row = connection.execute(
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
              AND status = 'sent'
            ORDER BY sent_at DESC
            LIMIT 1
            """,
            (book_id,),
        ).fetchone()

    if row is None:
        return None

    return Question(
        id=row["id"],
        book_id=row["book_id"],
        question=row["question"],
        topic=row["topic"],
        difficulty=row["difficulty"],
        reference_context=row["reference_context"],
    )