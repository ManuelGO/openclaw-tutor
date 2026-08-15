import argparse
from tutor.books.repository import get_book_by_title
from tutor.learning.service import (
    next_question,
    submit_active_answer,
)

def handle_next_question(book_title: str) -> None:
    book = get_book_by_title(book_title)

    if book is None:
        raise SystemExit(f'Book not found: "{book_title}"')

    question = next_question(book.id)

    if question is None:
        print("No pending questions.")
        return

    print(f"\n🧠 {book.title}\n")
    print(question.question)
    print(f"\nDifficulty: {question.difficulty}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tutor",
        description="Personal learning tutor",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    next_parser = subparsers.add_parser(
        "next-question",
        help="Get the next pending question",
    )
    
    answer_parser = subparsers.add_parser(
    "answer",
    help="Answer the active question",
    )   

    answer_parser.add_argument(
        "--book",
        required=True,
        help="Book title",
    )

    answer_parser.add_argument(
        "--text",
        required=True,
        help="Student answer",
    )

    next_parser.add_argument(
        "--book",
        required=True,
        help="Book title",
    )

    args = parser.parse_args()

    if args.command == "next-question":
        handle_next_question(args.book)

    elif args.command == "answer":
        handle_answer(
            book_title=args.book,
            text=args.text,
    )
        
def handle_answer(
    book_title: str,
    text: str,
) -> None:
    book = get_book_by_title(book_title)

    if book is None:
        raise SystemExit(f'Book not found: "{book_title}"')

    try:
        evaluation = submit_active_answer(
            book_id=book.id,
            text=text,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"\nScore: {evaluation.score}/100")

    print(f"\nFeedback:\n{evaluation.feedback}")

    print("\nStrengths:")
    for strength in evaluation.strengths:
        print(f"- {strength}")

    print("\nGaps:")
    for gap in evaluation.gaps:
        print(f"- {gap}")


if __name__ == "__main__":
    main()