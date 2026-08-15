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