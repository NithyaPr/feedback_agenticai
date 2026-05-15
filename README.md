# Feedback System

A LangGraph-powered feedback collection and analysis system with FastAPI. Supports dual database backends — SQLite (local) and PostgreSQL + pgvector (AWS production) — with semantic search and multi-LLM provider support.

## Features

- **Feedback Submission**: Users submit feedback with NPS scores (1-10)
- **AI Auto-Categorization**: LLM classifies feedback into categories using few-shot examples
- **AI Acknowledgment**: LLM generates polite responses with optional knowledge base references
- **Smart Routing**: Feedback flagged for review (needs_review) is routed to appropriate support team
- **Support Queue**: Review tickets with notes, follow-up, and resolve workflow
- **User POV Preview**: See all feedbacks as a user would — completed/pending/resolved statuses
- **PM Chat**: Ask questions about feedback trends — semantic search via pgvector or in-process embeddings
- **Semantic Search**: Embeddings stored in SQLite BLOBs or PostgreSQL vector columns
- **Knowledge Base**: Policy articles matched by keywords, referenced in AI responses
- **Multi-Provider**: Switch between Ollama (local), OpenAI, and Google Gemini
- **Theme Customization**: Light/Dark modes with custom color presets
- **Duplicate Detection**: FTS5 (SQLite) or `to_tsvector` (PostgreSQL) full-text search

## Tech Stack

- **FastAPI** — REST API framework
- **LangGraph** — Workflow orchestration (StateGraph)
- **SQLite** (local) / **PostgreSQL + pgvector** (AWS) — Database
- **Ollama (default)** — Local LLM + embeddings via nomic-embed-text
- **OpenAI / Google Gemini** — Alternative cloud providers
- **HTML/CSS/JS** — Single-page application frontend
- **Docker** — Containerized deployment

## Quick Start (Local)

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) (for default provider)

### Setup

```bash
# Clone and enter project
cd feedback_agenticAI

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull gemma2:2b        # For chat/analysis
ollama pull nomic-embed-text # For embeddings

# Seed demo data
python scripts/seed_demo.py

# Run server
python -m app.main
```

Open http://localhost:8000

## Docker (AWS Deployment)

```bash
# Build image
docker build -t feedback-system .

# Run with PostgreSQL (set DATABASE_URL env var)
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@rds-host:5432/feedback \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  feedback-system
```

### AWS Deployment Steps

1. Create RDS PostgreSQL instance with `pgvector` extension
2. Set `DATABASE_URL` environment variable in ECS/App Runner
3. Use OpenAI/Gemini as LLM provider (no Ollama needed on AWS)
4. Push Docker image to ECR and deploy

## Configuration

Edit `.env`:
```env
# Backend (leave empty for local SQLite)
DATABASE_URL=

# PostgreSQL for AWS
# DATABASE_URL=postgresql://user:password@host:5432/feedback

# LLM Provider
LLM_PROVIDER=ollama              # ollama, openai, google
EMBEDDING_PROVIDER=ollama        # ollama, openai, google
OLLAMA_MODEL=gemma2:2b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

## Usage

### Submit Feedback
1. Go to **Submit Feedback** tab
2. Enter feedback text, NPS score (1-10), optional product name
3. Submit → AI response with categories + routing

### Support Queue
1. Go to **Support** tab — shows review tickets needing attention
2. Select a card → Action bar appears at bottom
3. **View Details** — Full feedback + AI response in modal
4. **Add Notes** — Internal timestamped note
5. **Send Follow-up** — Final response to user + auto-resolve
6. **Resolve** — Mark as resolved

### PM Chat
1. Go to **PM Chat** tab
2. Apply optional filters (product, NPS range, category)
3. Ask questions like:
   - "What are users struggling with?"
   - "What features are most requested?"
   - "Show me delivery complaints"

### User POV Preview
1. In the Support tab, click **Preview as User**
2. Shows all feedbacks — completed (no ticket), pending, or resolved

## Project Structure

```
├── app/
│   ├── api/               # REST endpoints
│   ├── graph/             # LangGraph workflows
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic + database
│   ├── static/            # Frontend (SPA)
│   └── main.py            # FastAPI app
├── config/                # Settings + category configs
├── scripts/               # Seed data utilities
├── docs/                  # Architecture documentation
├── Dockerfile             # Container image
├── requirements.txt
├── .env
└── feedback.db            # SQLite database (auto-created, local only)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/feedback` | POST | Submit feedback |
| `/api/chat` | POST | PM Chat with semantic search |
| `/api/reviews` | GET | List review tickets |
| `/api/reviews/{id}` | GET/PUT | Get/update review |
| `/api/preview-user` | GET | All feedbacks with status |
| `/api/stats` | GET | Aggregate statistics |
| `/api/categories` | GET | Categories + few-shot examples |
| `/api/provider` | GET/PUT | Provider configuration |
| `/api/teams` | GET | Support teams |
| `/health` | GET | Health check |

## Documentation

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture, data flow, database schema, workflow diagrams, and AWS deployment guide.
