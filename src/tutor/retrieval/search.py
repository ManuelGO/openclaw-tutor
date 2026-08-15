import tutor.config  # noqa: F401
from openai import OpenAI

from openai.types.vector_store_search_response import VectorStoreSearchResponse
from tutor.books.models import Book

def search(
    book: Book,
    query: str,
    limit: int = 5,
) -> list[VectorStoreSearchResponse]:
    client = OpenAI()

    results = client.vector_stores.search(
        vector_store_id=book.vector_store_id,
        query=query,
    )

    return results.data[:limit]

if __name__ == "__main__":
    from tutor.books.repository import get_book_by_title

    book = get_book_by_title("Fluent Python")

    if book is None:
        raise RuntimeError("Fluent Python is not registered")

    results = search(
        book=book,
        query="What is the difference between an iterable and an iterator?",
    )

    for index, result in enumerate(results, start=1):
        print(f"\n--- RESULT {index} ---")
        print(f"Score: {result.score:.4f}")

        for content in result.content:
            if content.type == "text":
                print(content.text)