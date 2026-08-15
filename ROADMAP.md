# OpenClaw Tutor Roadmap

The MVP proves the core learning loop for one learner, one book and a predefined topic.

The next stages evolve the project from a personal tutor into a reusable multi-user learning platform.

---

## v0.1 — Personal Tutor MVP ✅

Status: **Complete**

### Learning engine

- [x] PDF ingestion
- [x] OpenAI Vector Store integration
- [x] Semantic retrieval
- [x] RAG-grounded question generation
- [x] Structured question output
- [x] RAG-grounded answer evaluation
- [x] Score, feedback, strengths and gaps

### Persistence

- [x] SQLite database
- [x] Books
- [x] Questions
- [x] Answers
- [x] Evaluations
- [x] Question lifecycle
- [x] Foreign-key enforcement
- [x] Transactional answer/evaluation persistence

### Workflow

- [x] CLI
- [x] One active question at a time
- [x] Automatic question batch generation
- [x] Reuse active questions
- [x] OpenClaw integration
- [x] Custom OpenClaw tutor skill
- [x] WhatsApp interaction
- [x] Scheduled study sessions

---

## v0.2 — Dynamic books and topics

### Goal

Remove hard-coded knowledge about *Fluent Python* and individual topics from the learning workflow.

### Books

- [ ] Add a CLI command for book registration
- [ ] Upload/index a book automatically
- [ ] Store vector store/file references automatically
- [ ] List available books
- [ ] Enable/disable books
- [ ] Remove a book safely
- [ ] Track ingestion/indexing status
- [ ] Store book metadata

Target experience:

```bash
tutor books add ./books/fluent-python.pdf \
  --title "Fluent Python"
```

Then:

```bash
tutor books list
```

### Topic selection

- [ ] Remove hard-coded topic from scheduled jobs
- [ ] Allow topic selection through conversation
- [ ] Store topics associated with books
- [ ] Discover candidate topics from book content
- [ ] Track progress by topic
- [ ] Allow "continue where I left off"
- [ ] Allow mixed-topic review sessions

Target conversation:

```text
User:
I want to study.

Tutor:
Which book?

1. Fluent Python
2. Designing Data-Intensive Applications

User:
Fluent Python

Tutor:
Which topic?

1. Iterators
2. Data classes
3. Protocols
4. Coroutines
5. Review weak areas
```

---

## v0.3 — Multi-user support

### Goal

Move from a single personal learner to multiple independent users.

Introduce a `User` domain entity.

Potential model:

```text
User
 ├── id
 ├── name
 ├── phone
 ├── email
 ├── timezone
 ├── preferred_channel
 └── status
```

### User management

- [ ] Create users
- [ ] Identify users by phone number
- [ ] Identify users by email
- [ ] Associate external channel identities with internal user IDs
- [ ] Store user timezone
- [ ] Store communication preferences
- [ ] Enable/disable users

Target CLI:

```bash
tutor users add \
  --name "User Name" \
  --phone "+34..." \
  --email "user@example.com"
```

### User-specific learning state

Questions, answers and evaluations must become associated with a learner.

Conceptually:

```text
User
 │
 ├── Enrollment
 │      └── Book
 │
 ├── Question assignments
 ├── Answers
 ├── Evaluations
 └── Progress
```

- [ ] Associate learning sessions with users
- [ ] Maintain independent active questions
- [ ] Maintain independent learning history
- [ ] Maintain independent topic progress
- [ ] Maintain independent schedules

---

## v0.4 — User-controlled learning

### Goal

Let learners control what they study through natural conversation.

Examples:

```text
"Let's study Fluent Python."

"Ask me about protocols."

"I want to review iterators."

"Give me something difficult."

"Continue where we stopped."

"Switch to another book."

"Review the topics I'm weakest at."
```

### Features

- [ ] Select book conversationally
- [ ] Select topic conversationally
- [ ] Select difficulty
- [ ] Select number of questions
- [ ] Start/stop a study session
- [ ] Pause scheduled learning
- [ ] Change study schedule
- [ ] Request review sessions
- [ ] Ask for current progress

OpenClaw should translate conversational intent into operations on the tutor application rather than implementing the learning rules itself.

---

## v0.5 — Adaptive learning

### Goal

Use accumulated learning history to decide what the learner should study next.

- [ ] Topic mastery scores
- [ ] Question history
- [ ] Detect weak concepts
- [ ] Avoid semantically duplicate questions
- [ ] Difficulty adaptation
- [ ] Spaced repetition
- [ ] Review scheduling
- [ ] Weight questions by previous performance
- [ ] Track improvement over time

Instead of:

```text
schedule → next available question
```

the system evolves toward:

```text
learning history
       +
topic mastery
       +
time since review
       +
previous mistakes
       ↓
next best learning activity
```

---

## v0.6 — Multi-channel delivery

### Goal

Decouple learner identity from the communication channel.

Potential channels:

- WhatsApp
- Email
- Web
- Slack
- Microsoft Teams

A learner could eventually have:

```text
User
 ├── WhatsApp identity
 ├── Email identity
 └── other channel identities
```

while maintaining one shared learning history.

---

## v0.7 — Progress and analytics

- [ ] Overall progress
- [ ] Progress by book
- [ ] Progress by topic
- [ ] Average evaluation score
- [ ] Weakest topics
- [ ] Strongest topics
- [ ] Study streaks
- [ ] Questions answered over time
- [ ] Score evolution
- [ ] Review effectiveness

Potential command:

```text
"How am I doing with Fluent Python?"
```

Potential response:

```text
Fluent Python

Questions answered: 47
Average score: 82
Strongest topic: Iterators
Weakest topic: Protocols
Due for review: Data model
```

---

## v1.0 — Reusable learning platform

The project reaches v1.0 when:

- Multiple users can be registered easily
- Users can be identified through phone and/or email
- Books can be added without code changes
- Users can select their book
- Users can select topics
- Each user has independent learning state
- Scheduling is configurable per user
- Adaptive review is available
- Multiple communication channels can share the same learning state
- Deployment no longer assumes a single developer workstation

Target architecture:

```text
                       ┌───────────────────┐
                       │      Users        │
                       └─────────┬─────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
              WhatsApp         Email           Web
                  │              │              │
                  └──────────────┼──────────────┘
                                 │
                              OpenClaw
                                 │
                                 ▼
                       ┌───────────────────┐
                       │   Tutor Service   │
                       ├───────────────────┤
                       │ Study workflow    │
                       │ User management   │
                       │ Book management   │
                       │ Topic selection   │
                       │ Adaptive learning │
                       └──────┬───────┬────┘
                              │       │
                         Database    RAG
                              │       │
                              │    Vector Stores
                              │       │
                              └── Books
```

---

## Longer-term ideas

These are intentionally outside the current roadmap and should only be considered after the core multi-user architecture is stable.

- Web dashboard
- Learning analytics visualization
- Book/chapter progress maps
- Automatic chapter detection
- Cross-book learning paths
- Course material in addition to books
- Coding exercises with executable validation
- Repository/codebase learning sources
- Voice interaction
- Teacher/admin accounts
- Shared study programs
- Exportable learning reports
