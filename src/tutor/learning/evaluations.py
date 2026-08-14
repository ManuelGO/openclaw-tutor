from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerEvaluation:
    id: str
    answer_id: str
    score: int
    feedback: str
    strengths: list[str]
    gaps: list[str]