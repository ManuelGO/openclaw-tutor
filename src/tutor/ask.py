from openai import OpenAI
import sys
from tutor.retrieval.search import search
from tutor.books.models import Book
import tutor.config  # noqa: F401

def build_context(results) -> str:
    chunks = []

    for result in results:
        for content in result.content:
            if content.type == "text":
                chunks.append(content.text)

    return "\n\n---\n\n".join(chunks)

def ask(book: Book, question: str) -> str:
    results = results = search(
                book=book,
                query=question,
                limit=3,
            )
    context = build_context(results)

    client = OpenAI()
    response = client.responses.create(
    model="gpt-5.1",
        instructions=(
            "You are a tutor helping a student study {book.title}. "
            "Answer using only the reference material provided. "
            "If the reference material does not contain enough information "
            "to answer the question, say so explicitly."
        ),
        input=f"""
    QUESTION:
    {question}

    REFERENCE MATERIAL:
    {context}
    """,
        )

    return response.output_text

if __name__ == "__main__":
    import sys

    from tutor.books.repository import get_book_by_title

    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python3 -m tutor.ask "your question"'
        )

    book = get_book_by_title("Fluent Python")

    if book is None:
        raise RuntimeError("Fluent Python is not registered")

    question = " ".join(sys.argv[1:])
    answer = ask(book, question)

    print("\n--- ANSWER ---\n")
    print(answer)