from uuid import uuid4

from pydantic import BaseModel, Field
from openai import OpenAI
from tutor.learning.answers import Answer
from tutor.learning.evaluations import AnswerEvaluation
from tutor.learning.questions import Question
import tutor.config  # noqa: F401


class Evaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    gaps: list[str]


def evaluate(
    question: Question,
    answer: Answer,
) -> Evaluation:
    client = OpenAI()

    response = client.responses.parse(
        model="gpt-5.1",
        instructions=(
            "You are evaluating a student's answer to a technical "
            "study question. "
            "Evaluate the answer using only the supplied reference material. "
            "Do not reward information that cannot be supported by the "
            "reference material. "
            "Score the answer from 0 to 100 based primarily on correctness "
            "and completeness. "
            "Clearly identify what the student understood and what important "
            "points are missing or incorrect. "
            "Be technically precise. Do not generalize exception behavior: "
            "Distinguish IndexError, StopIteration, and TypeError when relevant. "
            "and TypeError when relevant. "
            "Give concise, educational feedback."
        ),
        input=f"""
        QUESTION:
        {question.question}

        STUDENT ANSWER:
        {answer.answer}

        REFERENCE MATERIAL:
        {question.reference_context}
        """,
                text_format=Evaluation,
            )

    return response.output_parsed



def build_evaluation(
    answer: Answer,
    evaluation: Evaluation,
) -> AnswerEvaluation:
    return AnswerEvaluation(
        id=str(uuid4()),
        answer_id=answer.id,
        score=evaluation.score,
        feedback=evaluation.feedback,
        strengths=evaluation.strengths,
        gaps=evaluation.gaps,
    )