from pydantic import BaseModel, Field
from openai import OpenAI
from tutor.learning.answers import Answer
from tutor.learning.questions import Question
import tutor.config  # noqa: F401

class Evaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    gaps: list[str]
    
from uuid import uuid4
from tutor.learning.evaluations import AnswerEvaluation

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


if __name__ == "__main__":
    from tutor.learning.answers_repository import get_answers_for_question
    from tutor.learning.questions_repository import get_question

    question_id = "cebec66c-6dbf-4203-962a-8fb551c0c5a6"

    question = get_question(question_id)

    if question is None:
        raise RuntimeError("Question not found")

    answers = get_answers_for_question(question_id)

    if not answers:
        raise RuntimeError("No answers found")

    evaluation = evaluate(
        question=question,
        answer=answers[-1],
    )

    print(f"\nScore: {evaluation.score}/100")
    print(f"\nFeedback:\n{evaluation.feedback}")

    print("\nStrengths:")
    for strength in evaluation.strengths:
        print(f"- {strength}")

    print("\nGaps:")
    for gap in evaluation.gaps:
        print(f"- {gap}")