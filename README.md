# OpenClaw Tutor

An AI-powered personal learning tutor that turns technical books into an interactive, scheduled study experience.

The tutor uses Retrieval-Augmented Generation (RAG) to generate questions grounded in source material, evaluates the learner's answers against that material, tracks learning history, and uses OpenClaw to deliver the experience through WhatsApp.

The current MVP uses *Fluent Python* as its first knowledge source.

## Why this project?

Reading a technical book is easy.

Remembering and applying what you read weeks later is much harder.

OpenClaw Tutor turns passive reading into active recall:

1. Retrieve relevant material from the book.
2. Generate understanding-oriented questions.
3. Deliver a question to the learner.
4. Receive the answer conversationally.
5. Evaluate it against the source material.
6. Return a score and detailed feedback.
7. Persist the learning history.
8. Continue the learning cycle automatically.

The learner does not need to interact with a CLI or learning platform. The current interface is simply WhatsApp.

## Current MVP

The MVP supports the complete learning loop:

- PDF book ingestion
- OpenAI Vector Store for semantic retrieval
- RAG-based question generation
- Structured question generation with Pydantic
- SQLite persistence
- Question lifecycle:
  - `pending`
  - `sent`
  - `answered`
- One active question at a time
- RAG-grounded answer evaluation
- Numerical scores
- Detailed feedback
- Strengths and knowledge gaps
- Persistent answer/evaluation history
- Automatic question batch generation
- CLI interface
- OpenClaw integration
- WhatsApp delivery
- Natural-language answer handling
- Scheduled study sessions
- Automatic continuation of existing sessions

## Architecture

```text
                         ┌─────────────────┐
                         │   Technical PDF │
                         │  Fluent Python  │
                         └────────┬────────┘
                                  │
                              ingestion
                                  │
                                  ▼
                       ┌────────────────────┐
                       │ OpenAI Vector Store│
                       │ semantic retrieval │
                       └─────────┬──────────┘
                                 │
                                 │ RAG
                                 ▼
                    ┌─────────────────────────┐
                    │    OpenClaw Tutor       │
                    │                         │
                    │ question generation     │
                    │ answer evaluation       │
                    │ learning workflow       │
                    └───────┬─────────┬───────┘
                            │         │
                            │         │
                            ▼         ▼
                      ┌─────────┐  ┌──────────┐
                      │ SQLite  │  │ OpenClaw │
                      │         │  │  Agent   │
                      └─────────┘  └────┬─────┘
                                        │
                              scheduled / interactive
                                        │
                                        ▼
                                   ┌──────────┐
                                   │ WhatsApp │
                                   └────┬─────┘
                                        │
                                        ▼
                                     Learner
```

## Requirements

- Python 3.12+
- An OpenAI API key
- A PDF of the book you want to study

## Setup

Create the virtual environment and install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create a `.env` file at the project root:

```bash
OPENAI_API_KEY=sk-...
```

`.env` and other secrets must never be committed to the repository.

Place the source PDF in `books/`. The ingestion script currently expects:

```text
books/Fluent Python.pdf
```

Book files are gitignored: the repository never stores copyrighted source material.

### 1. Initialize the database

```bash
python3 -m tutor.db.database
```

This creates `data/tutor.db` with the `books`, `questions`, `answers` and `evaluations` tables, including the `status` and `sent_at` columns that drive the question lifecycle.

### 2. Ingest the book

```bash
python3 -m tutor.ingestion.ingest
```

This uploads the PDF to an OpenAI Vector Store, indexes it, and saves the resulting vector store ID to `data/vector_store.json`. The script is idempotent: if a vector store ID is already saved, it exits without re-uploading.

### 3. Register the book

```bash
python3 -m tutor.books.repository
```

This reads `data/vector_store.json` and registers the book in the `books` table, linking the title to its vector store. The title defaults to *Fluent Python*; pass another as an argument. Running it again returns the existing book instead of registering a duplicate.

## Usage

### Start or continue a study session

```bash
python3 -m tutor.cli study \
  --book "Fluent Python" \
  --topic "iterables, iterators and the iter function"
```

Prints the active question and its difficulty.

### Answer the active question

```bash
python3 -m tutor.cli answer \
  --book "Fluent Python" \
  --text "An iterable is any object that implements __iter__..."
```

Prints the score, feedback, strengths and gaps.

### Show the current question without generating a new batch

```bash
python3 -m tutor.cli next-question --book "Fluent Python"
```

Returns the active question, or activates the next pending one. Prints `No pending questions.` when the batch is exhausted — unlike `study`, it never generates new questions.

### Ask a free-form question about the book

```bash
python3 -m tutor.ask "Fluent Python" \
  "What is the difference between an iterable and an iterator?"
```

A RAG-grounded lookup that sits outside the learning loop: nothing is persisted and no question lifecycle is touched.

## Learning workflow

The service first checks whether a question is already active.

```text
study()
   │
   ├── active question exists
   │       └── return it
   │
   ├── pending question exists
   │       └── mark as sent and return it
   │
   └── no questions available
           │
           ├── retrieve source material
           ├── generate a new batch
           ├── persist questions
           └── activate the first question
```

This makes the operation safe to invoke repeatedly from a scheduler: an existing active question is reused instead of continuously generating new questions.

Batches default to four questions.

## Answer evaluation

When the learner answers a question, the tutor:

1. Finds the active question.
2. Retrieves its reference context.
3. Creates an `Answer`.
4. Evaluates the answer against the source material.
5. Produces structured feedback.
6. Atomically persists the answer and evaluation.
7. Marks the question as answered.

An evaluation contains:

- `score`
- `feedback`
- `strengths`
- `gaps`

Example:

```text
Score: 88/100

Feedback:
...

Strengths:
- ...

Gaps:
- ...
```

The evaluation is grounded in the book rather than relying solely on the model's general knowledge. The reference context is captured at generation time and stored alongside the question, so an answer is always evaluated against the exact material the question came from.

## Persistence

SQLite stores the learning state locally.

Current entities include:

- `Book`
- `Question`
- `Answer`
- `Evaluation`

Questions have a lifecycle:

```text
pending → sent → answered
```

Database foreign-key enforcement is enabled for every application connection.

Answer and evaluation persistence is transactional so that an external API failure does not leave a partially completed learning interaction in the database. The model call happens *before* the transaction opens: if OpenAI fails, nothing has been written.

## OpenClaw integration

OpenClaw acts as the conversational and scheduling layer.

A custom personal-tutor skill teaches the agent how to interact with the local tutor application.

OpenClaw is responsible for:

- interacting with the learner
- invoking the tutor CLI
- delivering questions
- passing answers to the tutor
- returning evaluation results
- scheduling study sessions

The tutor application remains responsible for the learning business logic.

This separation keeps OpenClaw replaceable as an orchestration/interface layer.

## Scheduled learning

The MVP currently schedules study opportunities three times per day:

- 09:00
- 15:00
- 20:00

Time zone: `Europe/Madrid`

Only one question can be active at a time.

If the learner has not answered the previous question, the next scheduled execution returns the same active question instead of consuming another one.

When no pending questions remain, the tutor automatically generates a new batch.

## Project structure

```text
openclaw-tutor/
├── books/                      # source PDFs (gitignored)
├── data/
│   ├── tutor.db                # SQLite learning state
│   └── vector_store.json       # saved vector store ID
├── src/
│   └── tutor/
│       ├── books/              # Book model and repository
│       ├── db/                 # connection and schema
│       ├── ingestion/          # PDF → Vector Store
│       ├── learning/           # questions, answers, evaluation, service
│       ├── retrieval/          # vector store search
│       ├── ask.py              # free-form RAG question
│       ├── cli.py              # command-line entry point
│       └── config.py           # .env loading
├── tests/
├── .env                        # gitignored
├── pyproject.toml
├── README.md
└── ROADMAP.md
```

## Tech stack

- Python 3.12
- OpenAI API (`gpt-5.1`, Responses API with structured outputs)
- OpenAI Vector Stores
- Retrieval-Augmented Generation (RAG)
- Pydantic
- SQLite
- OpenClaw
- WhatsApp

## Design principles

### Ground answers in source material

The tutor should evaluate knowledge of the selected learning material, not merely whether an LLM considers an answer plausible.

### Keep orchestration separate from domain logic

OpenClaw handles communication and scheduling.

The Python application owns learning state, retrieval, generation and evaluation.

### Persist learning history

Questions and answers are not disposable chat messages. They form a dataset that can later drive adaptive learning and spaced repetition.

### Fail before mutating state

External model calls happen before transactional persistence where appropriate, preventing failed evaluations from leaving inconsistent learning state.

### Keep the interface replaceable

WhatsApp is currently the user interface, but the learning engine does not depend on WhatsApp.

Future interfaces could include email, web applications or other messaging platforms.

## Status

MVP: complete

The complete end-to-end flow has been validated:

```text
Book
  ↓
Vector Store
  ↓
RAG
  ↓
Question
  ↓
SQLite
  ↓
OpenClaw
  ↓
WhatsApp
  ↓
Learner answer
  ↓
OpenClaw
  ↓
RAG evaluation
  ↓
Score + feedback
  ↓
SQLite
```

### Known limitations

- Ingestion is hardcoded to `books/Fluent Python.pdf`; adding a second book requires code changes.
- `tests/` is empty; `pytest` is installed but no tests are written yet.

Both are addressed in [ROADMAP.md](ROADMAP.md), which lays out the path from this single-learner MVP to a reusable multi-user platform.
