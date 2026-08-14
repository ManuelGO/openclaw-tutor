from pathlib import Path
import json

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = PROJECT_ROOT / "books" / "Fluent Python.pdf"
STATE_PATH = PROJECT_ROOT / "data" / "vector_store.json"


def load_vector_store_id() -> str | None:
    if not STATE_PATH.exists():
        return None

    data = json.loads(STATE_PATH.read_text())
    return data["vector_store_id"]


def save_vector_store_id(vector_store_id: str) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    STATE_PATH.write_text(
        json.dumps(
            {"vector_store_id": vector_store_id},
            indent=2,
        )
    )


def main() -> None:
    load_dotenv()

    client = OpenAI()

    vector_store_id = load_vector_store_id()

    if vector_store_id:
        print(f"Vector Store existente: {vector_store_id}")
        return

    if not BOOK_PATH.exists():
        raise FileNotFoundError(f"No encuentro el libro: {BOOK_PATH}")

    print(f"Creando Vector Store para {BOOK_PATH.name}...")

    vector_store = client.vector_stores.create(
        name="Fluent Python"
    )

    print(f"Vector Store creado: {vector_store.id}")
    print("Subiendo e indexando libro...")

    with BOOK_PATH.open("rb") as book:
        result = client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=book,
        )

    print(f"Estado de indexación: {result.status}")

    save_vector_store_id(vector_store.id)

    print(f"Vector Store ID guardado en {STATE_PATH}")


if __name__ == "__main__":
    main()