from tutor.db.database import get_connection
from tutor.learning.answers import Answer


def save_answer(answer: Answer) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO answers (
                id,
                question_id,
                answer
            )
            VALUES (?, ?, ?)
            """,
            (
                answer.id,
                answer.question_id,
                answer.answer,
            ),
        )
        
def get_answers_for_question(
    question_id: str,
) -> list[Answer]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, question_id, answer
            FROM answers
            WHERE question_id = ?
            ORDER BY created_at
            """,
            (question_id,),
        ).fetchall()

    return [
        Answer(
            id=row["id"],
            question_id=row["question_id"],
            answer=row["answer"],
        )
        for row in rows
    ]