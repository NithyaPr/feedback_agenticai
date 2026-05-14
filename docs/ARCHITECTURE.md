# Architecture Documentation

## Feedback Submission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER SUBMITS FEEDBACK                          │
│  (product, feedback_text, nps_score 1-10)                                    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI: /api/feedback                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  FeedbackRequest (Pydantic)                                         │    │
│  │  - product (optional)                                              │    │
│  │  - feedback_text                                                    │    │
│  │  - nps_score (1-10)                                                │    │
│  │  - user_id (optional)                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGRAPH WORKFLOW (StateGraph)                     │
│                                                                             │
│   ┌─────────────┐    ┌───────────────┐    ┌────────────────────┐           │
│   │  STORE      │───▶│   CATEGORIZE  │───▶│   GENERATE         │           │
│   │  FEEDBACK   │    │   (LLM)       │    │   RESPONSE (LLM)  │           │
│   └─────────────┘    └───────────────┘    └────────────────────┘           │
│        │                    │                      │                       │
│        ▼                    ▼                      ▼                       │
│   ┌─────────────┐    ┌───────────────┐    ┌────────────────────┐           │
│   │ Add to      │    │ Classify      │    │ Generate polite   │           │
│   │ ChromaDB    │    │ using LLM     │    │ acknowledgment    │           │
│   │ (vector     │    │ + few-shot    │    │ response          │           │
│   │  store)     │    │ examples      │    │                   │           │
│   └─────────────┘    └───────────────┘    └────────────────────┘           │
│                                                                             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RESPONSE TO UI                                 │
│  - success: true/false                                                     │
│  - llm_response (acknowledgment)                                           │
│  - categories (auto-detected, max 3)                                       │
│  - nps_score                                                                │
│  - timestamp                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Details

1. **User Input**: User provides feedback text and NPS score (1-10). Product name is optional.

2. **API Layer**: FastAPI receives `FeedbackRequest` and passes to workflow.

3. **LangGraph Workflow**: Three-node pipeline:
   - **Store Feedback Node**: Saves feedback to ChromaDB with metadata (product, NPS, timestamp)
   - **Categorize Node**: Uses LLM with few-shot examples to classify into max 3 categories
   - **Response Node**: Generates polite acknowledgment response using LLM

4. **Response**: Returns success status, LLM response, detected categories, and original NPS to UI.

---

## PM Chat Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PM CHATS WITH QUESTION                              │
│  (message, product_filter, min_nps, max_nps, categories_filter)            │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI: /api/chat                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ChatRequest                                                         │    │
│  │  - message                                                           │    │
│  │  - product_filter (optional)                                        │    │
│  │  - min_nps / max_nps (optional)                                     │    │
│  │  - categories (optional)                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGRAPH CHAT WORKFLOW                              │
│                                                                             │
│   ┌─────────────┐    ┌────────────────────┐                                │
│   │  RETRIEVE  │───▶│   GENERATE          │                                │
│   │  (ChromaDB) │    │   RESPONSE (LLM)   │                                │
│   └─────────────┘    └────────────────────┘                                │
│        │                    │                                               │
│        ▼                    ▼                                               │
│   ┌─────────────┐    ┌────────────────────┐                                │
│   │ Semantic    │    │ Answer PM's        │                                │
│   │ search in   │    │ question using     │                                │
│   │ ChromaDB   │    │ relevant feedbacks  │                                │
│   │ + filters  │    │ as context          │                                │
│   └─────────────┘    └────────────────────┘                                │
│                                                                             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RESPONSE TO UI                                 │
│  - success: true/false                                                     │
│  - response (LLM-generated answer)                                         │
│  - relevant_feedbacks (list of feedback used as context)                  │
│  - timestamp                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Details

1. **PM Query**: Product manager asks questions about user feedback with optional filters.

2. **API Layer**: FastAPI receives `ChatRequest` with message and optional filters (product, NPS range, categories).

3. **LangGraph Workflow**: Two-node pipeline:
   - **Retrieve Node**: Queries ChromaDB using semantic search with applied filters
   - **Response Node**: Uses LLM to answer PM's question using retrieved feedbacks as context

4. **Response**: Returns LLM-generated answer with relevant feedback excerpts for context.

---

## Provider Configuration

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│     OLLAMA      │     │     OPENAI     │     │  GOOGLE GEMINI │
│   (Local)       │     │   (Cloud)       │     │    (Cloud)     │
│                 │     │                 │     │                 │
│  LLM: llama3.2 │     │ LLM: gpt-4o-mini│     │ LLM: gemini-2.0│
│  Embed: nomic  │     │ Embed: text-emb │     │ Embed: text-emb│
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Chroma Vector DB     │
                    │   (./chroma_db)        │
                    └─────────────────────────┘
```

### Provider Details

| Provider | Chat Model | Embedding Model | Requirements |
|----------|------------|-----------------|--------------|
| Ollama (default) | llama3.2:1b | nomic-embed-text or llama3.2:1b | `ollama serve` running |
| OpenAI | gpt-4o-mini | text-embedding-3-small | `OPENAI_API_KEY` in .env |
| Google Gemini | gemini-2.0-flash | text-embedding-004 | `GOOGLE_API_KEY` in .env |

### Mixing Providers

Chat and embedding providers can be configured independently:
- Ollama (chat) + OpenAI (embeddings)
- Google Gemini (chat) + Ollama (embeddings)
- etc.

---

## Data Storage

### ChromaDB Schema

```
Collection: feedbacks

Document Fields:
- feedback_text (stored internally, not displayed)
- id (UUID)

Metadata:
- product (string)
- nps_score (int 1-10)
- timestamp (ISO datetime)
- user_id (string)
- categories (list of strings, max 3)
```

### Categories Configuration

Categories are defined in `config/categories.json`:
- Configurable category list
- Few-shot examples for better LLM classification
- Max 3 categories returned per feedback