from dataclasses import dataclass


@dataclass(frozen=True)
class Answer:
    id: str
    question_id: str
    answer: str