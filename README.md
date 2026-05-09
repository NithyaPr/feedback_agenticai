# Feedback System

A LangGraph-powered feedback collection and analysis system with FastAPI and Chroma vector database.

## Features

- **User Feedback Submission**: Users can submit feedback about products
- **AI Acknowledgment**: LLM generates polite responses to user feedback
- **Product Manager Chat**: PMs can chat with the system to analyze feedback trends
- **Vector Storage**: Feedbacks are stored in Chroma for semantic search
- **Theme Customization**: Light/Dark modes with custom color options

## Tech Stack

- **FastAPI**: REST API framework
- **LangGraph**: Workflow orchestration
- **Chroma**: Vector database for feedback storage
- **OpenAI**: LLM for responses (GPT-4o-mini + text-embedding-3-small)
- **HTML/JS/CSS**: Frontend UI

## Project Structure

```
.
├── app/
│   ├── api/               # API endpoints
│   │   ├── feedback.py    # POST /api/feedback
│   │   └── chat.py        # POST /api/chat
│   ├── graph/             # LangGraph workflow
│   │   ├── nodes.py       # Graph nodes
│   │   └── workflow.py    # Graph definitions
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── vector_store.py
│   │   └── llm_service.py
│   ├── static/            # Frontend files
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   └── main.py            # FastAPI app
├── config/
│   └── settings.py
├── requirements.txt
├── .env
└── README.md
```

## Setup

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Copy .env.example to .env and add your OpenAI API key
   copy .env.example .env
   ```
   Edit `.env` and set:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Run the server**:
   ```bash
   python -m app.main
   # or: uvicorn app.main:app --reload
   ```

5. **Access the UI**:
   Open http://localhost:8000 in your browser

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the web UI |
| `/api/feedback` | POST | Submit user feedback |
| `/api/chat` | POST | PM chat with feedback data |
| `/health` | GET | Health check |

## Usage

### Submitting Feedback
1. Open the web UI
2. Go to "Submit Feedback" tab
3. Enter product name and feedback
4. Click "Submit Feedback"
5. Receive AI-generated acknowledgment

### Product Manager Chat
1. Go to "PM Chat" tab
2. Optionally filter by product
3. Ask questions like:
   - "What are users struggling with?"
   - "What features do users like most?"
   - "What are the top complaints?"

### Customizing Theme
1. Click the settings icon (top right)
2. Toggle between Light/Dark mode
3. Choose preset themes (Ocean, Forest)
4. Customize individual colors
5. Settings auto-save to localStorage