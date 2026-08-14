import json
from uuid import uuid4
from tutor.db.database import get_connection
from tutor.learning.answers import Answer
from tutor.learning.evaluator import evaluate, build_evaluation
from tutor.learning.evaluations import AnswerEvaluation
from tutor.learning.questions import Question
from tutor.learning.questions_repository import (
    get_active_question,
    get_pending_questions,
    get_question,
    mark_question_sent,
)

def submit_answer(
    question_id: str,
    text: str,
) -> AnswerEvaluation:

    question = get_question(question_id)

    if question is None:
        raise ValueError(
            f"Question not found: {question_id}"
        )

    answer = Answer(
        id=str(uuid4()),
        question_id=question.id,
        answer=text,
    )

    # Nothing has been persisted yet.
    # If OpenAI fails, the database remains unchanged.
    generated_evaluation = evaluate(
        question=question,
        answer=answer,
    )

    evaluation = build_evaluation(
        answer=answer,
        evaluation=generated_evaluation,
    )
    # All database changes happen atomically.
    persist_answer_evaluation(
        answer=answer,
        evaluation=evaluation,
    )

    return evaluation

def next_question(book_id: str) -> Question | None:
    active_question = get_active_question(book_id)

    if active_question is not None:
        return active_question

    questions = get_pending_questions(
        book_id=book_id,
        limit=1,
    )

    if not questions:
        return None

    question = questions[0]

    mark_question_sent(question.id)

    return question

def submit_active_answer(
    book_id: str,
    text: str,
) -> AnswerEvaluation:

    question = get_active_question(book_id)

    if question is None:
        raise ValueError(
            f"No active question for book: {book_id}"
        )

    return submit_answer(
        question_id=question.id,
        text=text,
    )
def persist_answer_evaluation(
    answer: Answer,
    evaluation: AnswerEvaluation,
) -> None:
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

        connection.execute(
            """
            UPDATE questions
            SET status = 'answered'
            WHERE id = ?
            """,
            (answer.question_id,),
        )