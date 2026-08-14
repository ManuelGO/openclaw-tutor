from uuid import uuid4

from tutor.learning.answers import Answer
from tutor.learning.answers_repository import save_answer
from tutor.learning.evaluator import evaluate, build_evaluation
from tutor.learning.evaluations import AnswerEvaluation
from tutor.learning.evaluations_repository import save_evaluation
from tutor.learning.questions import Question
from tutor.learning.questions_repository import (
    get_active_question,
    get_pending_questions,
    get_question,
    mark_question_answered,
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

    save_answer(answer)
    save_evaluation(evaluation)
    mark_question_answered(question.id)

    return evaluation

def next_question(book_id: str) -> Question | None:
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
