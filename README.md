# Feedback System

A LangGraph-powered feedback collection and analysis system with FastAPI and Chroma vector database.

## Features

- **User Feedback Submission**: Users can submit feedback about products with NPS scores (1-10)
- **AI Auto-Categorization**: LLM automatically categorizes feedback using few-shot examples
- **AI Acknowledgment**: LLM generates polite responses to user feedback
- **Product Manager Chat**: PMs can chat with the system to analyze feedback trends with filters
- **Vector Storage**: Feedbacks are stored in Chroma for semantic search
- **Theme Customization**: Light/Dark modes with custom color options
- **Multi-Provider Support**: Switch between Ollama (local), OpenAI, and Google Gemini
- **Separate Chat & Embedding Models**: Configure different providers for LLM and embeddings

## Tech Stack

- **FastAPI**: REST API framework
- **LangGraph**: Workflow orchestration
- **Chroma**: Vector database for feedback storage
- **Ollama** (default): Local LLM (llama3.2:1b) + embeddings
- **OpenAI/Google Gemini**: Alternative cloud providers
- **HTML/JS/CSS**: Frontend UI

## Project Structure

```
.
├── app/
│   ├── api/               # API endpoints
│   │   ├── feedback.py    # POST /api/feedback
│   │   ├── chat.py        # POST /api/chat
│   │   └── categories.py  # Category CRUD
│   ├── graph/             # LangGraph workflow
│   │   ├── nodes.py       # Graph nodes
│   │   └── workflow.py    # Graph definitions
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── vector_store.py
│   │   ├── llm_service.py
│   │   └── category_service.py
│   ├── static/            # Frontend files
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   └── main.py            # FastAPI app
├── config/
│   ├── settings.py
│   └── categories.json    # Configurable categories + few-shot examples
├── requirements.txt
├── .env
└── README.md
```

## Setup

1. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ollama Setup** (default provider):
   - Install Ollama from https://ollama.com
   - Start Ollama server: `ollama serve`
   - Pull required models:
     ```bash
     ollama pull llama3.2:1b
     ollama pull nomic-embed-text  # For embeddings (optional)
     ```

4. **Configure environment**:
   Edit `.env`:
   ```
   LLM_PROVIDER=ollama
   EMBEDDING_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2:1b
   OLLAMA_EMBEDDING_MODEL=llama3.2:1b  # Use same model if nomic-embed-text not pulled
   ```

5. **Run the server**:
   ```bash
   python -m app.main
   # or: uvicorn app.main:app --reload
   ```

6. **Access the UI**:
   Open http://localhost:8000 in your browser

## Configuration

### LLM Providers

The system supports three providers with separate configurations for chat and embeddings:

| Provider | Chat Model | Embedding Model | Required Setup |
|----------|------------|-----------------|----------------|
| Ollama (default) | llama3.2:1b | nomic-embed-text | `ollama serve` running |
| OpenAI | gpt-4o-mini | text-embedding-3-small | `OPENAI_API_KEY` in .env |
| Google Gemini | gemini-2.0-flash | text-embedding-004 | `GOOGLE_API_KEY` in .env |

### Mixing Providers

You can use different providers for chat and embeddings:
- Ollama (chat) + OpenAI (embeddings)
- Google Gemini (chat) + Ollama (embeddings)
- etc.

### Categories

Categories are configurable via `config/categories.json`:
```json
{
  "categories": ["delivery", "billing", "product", "quality", "customer service"],
  "few_shot_examples": [
    {"feedback": "The package arrived damaged", "categories": ["delivery", "quality"]}
  ]
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the web UI |
| `/api/feedback` | POST | Submit user feedback with NPS |
| `/api/chat` | POST | PM chat with feedback data |
| `/api/categories` | GET | List all categories |
| `/api/categories` | POST | Add new category |
| `/api/categories` | PUT | Update category |
| `/api/categories` | DELETE | Delete category |
| `/health` | GET | Health check |

## Usage

### Submitting Feedback
1. Open the web UI
2. Go to "Submit Feedback" tab
3. Enter feedback text and NPS score (1-10)
4. Optionally enter product name
5. Click "Submit Feedback"
6. Receive AI-generated acknowledgment with auto-categorized tags

### Product Manager Chat
1. Go to "PM Chat" tab
2. Optionally filter by:
   - Product name
   - NPS range (min/max)
   - Category
3. Ask questions like:
   - "What are users struggling with?"
   - "What features do users like most?"
   - "What are the top complaints for delivery?"

### Customizing Theme
1. Click the settings icon (top right)
2. Toggle between Light/Dark mode
3. Choose preset themes (Ocean, Forest, etc.)
4. Customize individual colors
5. Settings auto-save to localStorage

### Provider Switching
1. Click the settings icon (top right)
2. Select LLM provider (Ollama/OpenAI/Gemini)
3. Select Embedding provider
4. Warning shown for Ollama to ensure server is running

## Maintenance

### Clean ChromaDB
To delete all stored feedback data:
```bash
# Windows
rmdir /s /q chroma_db

# Linux/Mac
rm -rf chroma_db
```

### View Stored Data
The vector database is stored in `chroma_db/` folder. Deleting this folder resets all feedback data.

## Recent Changes

- Added multi-provider support (Ollama, OpenAI, Google Gemini)
- Separate chat and embedding provider configurations
- Auto-categorization with few-shot examples (max 3 categories)
- Configurable categories via JSON file
- Provider switching UI in settings
- Readable chat response formatting
- LLM validation on startup for Ollama