import json

from tutor.db.database import get_connection
from tutor.learning.evaluations import AnswerEvaluation


def save_evaluation(evaluation: AnswerEvaluation) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO evaluations (
                id,
                answer_id,
                score,
                feedback,
                strengths,
                gaps
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation.id,
                evaluation.answer_id,
                evaluation.score,
                evaluation.feedback,
                json.dumps(evaluation.strengths),
                json.dumps(evaluation.gaps),
            ),
        )
        
def get_evaluation_for_answer(
    answer_id: str,
) -> AnswerEvaluation | None:

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                answer_id,
                score,
                feedback,
                strengths,
                gaps
            FROM evaluations
            WHERE answer_id = ?
            """,
            (answer_id,),
        ).fetchone()

    if row is None:
        return None

    return AnswerEvaluation(
        id=row["id"],
        answer_id=row["answer_id"],
        score=row["score"],
        feedback=row["feedback"],
        strengths=json.loads(row["strengths"]),
        gaps=json.loads(row["gaps"]),
    )