from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    id: str
    title: str
    vector_store_id: str