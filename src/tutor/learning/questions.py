from dataclasses import dataclass

from tutor.ask import build_context
from tutor.books.models import Book
from tutor.retrieval.search import search
from typing import Literal
from pydantic import BaseModel
import tutor.config  # noqa: F401
from openai import OpenAI
from uuid import uuid4
Difficulty = Literal["easy", "medium", "hard"]

@dataclass(frozen=True)
class Question:
    id: str
    book_id: str
    question: str
    topic: str
    difficulty: Difficulty
    reference_context: str

class GeneratedQuestion(BaseModel):
    question: str
    topic: str
    difficulty: Difficulty

class GeneratedQuestions(BaseModel):
    questions: list[GeneratedQuestion]
    
def get_reference_context(
    book: Book,
    topic: str,
) -> str:
    results = search(
        book=book,
        query=topic,
        limit=3,
    )

    return build_context(results)

def build_questions(
    book: Book,
    generated: GeneratedQuestions,
    context: str,
) -> list[Question]:
    return [
        Question(
            id=str(uuid4()),
            book_id=book.id,
            question=item.question,
            topic=item.topic,
            difficulty=item.difficulty,
            reference_context=context,
        )
        for item in generated.questions
    ]

def generate_questions(
    book: Book,
    topic: str,
    count: int = 4,
) -> list[Question]:
    context = get_reference_context(book, topic)
    client = OpenAI()
    response = client.responses.parse(
        model="gpt-5.1",
        instructions=(
            f"You are a tutor creating study questions about {book.title}. "
            "Create questions using only the supplied reference material. "
            "Questions should test understanding, not simple memorization. "
            "Do not provide the answers."
        ),
        input=f"""
        TOPIC:
        {topic}

        NUMBER OF QUESTIONS:
        {count}

        REFERENCE MATERIAL:
        {context}
        """,
        text_format=GeneratedQuestions,
    )

    return build_questions(
        book=book,
        generated=response.output_parsed,
        context=context,
    )
    
       
if __name__ == "__main__":
    from tutor.books.repository import get_book_by_title

    book = get_book_by_title("Fluent Python")

    if book is None:
        raise RuntimeError("Fluent Python is not registered")

    questions = generate_questions(
        book=book,
        topic="iterables, iterators and the iter function",
        count=4,
    )
    
    from tutor.learning.questions_repository import save_questions

    save_questions(questions)

    for index, question in enumerate(questions, start=1):
        print(f"\n{index}. [{question.difficulty}] {question.question}")
        print(f"   ID: {question.id}")
        print(f"   Book ID: {question.book_id}")
        print(f"   Topic: {question.topic}")