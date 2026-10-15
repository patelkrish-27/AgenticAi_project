# Enterprise IT Support Agentic RAG Copilot

An end-to-end Agentic AI application built by our group as our semester lab project. It is a deployable IT Support Copilot using **LangGraph, FastAPI, Pinecone, Tavily, HTML, CSS, and JavaScript** — with all LLM calls going to an **OpenAI-compatible endpoint (`nex-n2.5-mini`)**.

---

## 0. Course Project Info — Final 4 Weeks Lab Project

**Project Type Chosen: B. 🧠 Agentic AI Application**

> Develop an Agentic AI application/workflow using a pretrained LLM. The system goes beyond a simple chatbot or single LLM prompt and demonstrates an agentic workflow.

This project qualifies as **Path B** because it implements:

- [x] Planning / multi-step workflow via LangGraph (`Route → Retrieve → Grade → Web Search → Rewrite/Retry → Generate`)
- [x] Using tools/APIs (Pinecone retriever, Tavily web search)
- [x] Retrieving and using external information (private KB first, web fallback)
- [x] Maintaining context / state (`AgentState`: question, docs, grades, retries, trace, citations)
- [x] Making decisions based on intermediate results (KB grade GOOD/WEAK, web grade, retry guard)
- [x] Executing autonomously with audit trace + SQLite logging

### Group Members (Batch: same-batch group of 4)

| Sr. | Name | PRN |
|---|---|---|
| 1 | Krish Patel | 8022054486 |
| 2 | Niyati Thavrani | 8025064119 |
| 3 | Khushi Solanki | 8025064118 |
| 4 | Sumit Khapre | 8022055725 |

### Marks Mapping (Total 50)

- Attendance (10) — lab work over final 4 weeks, mandatory attendance
- Project Work and Viva (30) — demo scenarios in §8 + agentic trace in UI
- Practical file + project report (10) — this README serves as base for report; see §6 structure, §7 setup, §10 APIs

### 4-Week Lab Plan

- Week 1: Setup (§7 Steps 1-3), Pinecone + Tavily keys, run sample ingestion
- Week 2: Agentic workflow (§4) + chat API + UI trace verification
- Week 3: Document upload (`POST /api/ingest` + `X-Admin-Key`), audit DB, demo A-E
- Week 4: Viva prep, report writing, video/demo rehearsal

---

## 1. Business Problem

### Problem statement we chose
**NovaRetail**, a 3,000-employee retail company (case study for this project).

### Problem
The internal IT team maintains many documents: VPN instructions, password rules, MFA policy, software installation rules, laptop troubleshooting guides, and service-desk runbooks.

Employees still create repetitive support tickets because:

- They do not know where the correct document is.
- Traditional keyword search returns too many results.
- A normal chatbot may hallucinate an answer.
- Internal documents can be incomplete or outdated.
- Some questions require current vendor information from the public web.

### Example
An employee asks:

> **“How do I connect to the company VPN from home?”**

The answer exists in the private company KB, so the system should **not search the public internet**.

Another employee asks:

> **“What is the latest Microsoft Teams outage guidance?”**

The internal KB may not contain current outage information. The system should recognize weak private evidence, use an external search, grade that evidence, and answer with an external-source warning.

### Business Goal
Build a secure IT Support Copilot that:

1. Searches trusted private knowledge first.
2. Checks whether retrieved evidence is good enough.
3. Uses web search only when private knowledge is insufficient.
4. Rewrites weak queries and retries.
5. Generates grounded answers.
6. Shows the decision path for transparency and debugging.
7. Lets authorized staff add new company documents.

---

## 2. Why This Is an Agentic Project

A simple chatbot answers from a single prompt. Our system breaks the task into steps and acts on intermediate results. We designed it in layers, from problem study to a working product:

```text
Customer Problem
      ↓
Discovery & Requirements
      ↓
Solution Architecture
      ↓
Data / Knowledge Integration
      ↓
Agentic RAG Development
      ↓
API Development
      ↓
User Interface
      ↓
Security + Audit + Testing
      ↓
Deployment
      ↓
Observe + Improve
```

This repository demonstrates each layer.

---

## 3. Simple Architecture

```text
                   ┌─────────────────────┐
                   │   Employee / User   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ HTML/CSS/JavaScript │
                   │      Web UI         │
                   └──────────┬──────────┘
                              │ POST /api/chat
                              ▼
                   ┌─────────────────────┐
                   │       FastAPI       │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     LangGraph       │
                   │ Agentic RAG Control │
                   └──────────┬──────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
       ┌───────────────┐              ┌──────────────┐
       │ Private KB    │              │ Tavily Web   │
       │ Pinecone      │              │ Search       │
       └───────┬───────┘              └──────┬───────┘
               │                             │
               └──────────────┬──────────────┘
                              ▼
                      ┌────────────────┐
                      │ nex-n2.5-mini  │
                      │ OpenAI-compat. │
                      │ Grounded Answer│
                      └────────────────┘
```

---

## 4. Agentic RAG Workflow

Our agent follows this control flow, implemented in `app/rag/workflow.py`:

```text
Question
   ↓
[1] Route Question
   ├── Greeting / simple chat ─────────────→ Direct Answer
   │
   └── IT support question
                ↓
[2] Retrieve from Private Pinecone KB
                ↓
[3] Grade Private Evidence
       ┌────────┴────────┐
       │                 │
     GOOD               WEAK
       │                 │
       ▼                 ▼
Generate from KB    [4] Tavily Web Search
                         ↓
                  [5] Grade Web Evidence
                    ┌────┴─────┐
                    │          │
                  GOOD        WEAK
                    │          │
                    ▼          ▼
              Generate Web  [6] Rewrite Query
                               ↓
                         Retry Private KB
                               ↓
                        Max retry reached?
                               ↓
                    Insufficient Evidence
```

### Why Agentic?

Normal RAG does approximately this:

```text
Question → Retrieve → Generate
```

This project makes decisions:

```text
Question
 → Route
 → Retrieve
 → Evaluate evidence
 → Choose KB or Web
 → Rewrite if needed
 → Retry
 → Generate grounded answer
```

The system therefore controls **what to do next** based on its current state.

---

## 5. Main Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent workflow | LangGraph | Stateful routing and conditional decisions |
| LLM | `nex-n2.5-mini` via OpenAI-compatible endpoint | Routing, grading, rewriting, answer generation |
| LLM endpoint | `OPENAI_BASE_URL` (ngrok `/v1`) | All `ChatOpenAI` + `OpenAIEmbeddings` calls go here |
| Embeddings | OpenAI `text-embedding-3-small` | 1536-dimensional vectors (via same base URL) |
| Vector DB | Pinecone | Private enterprise knowledge base |
| External search | Tavily | Fallback when company KB is insufficient |
| API | FastAPI | Backend and REST endpoints |
| Frontend | HTML/CSS/JavaScript | Employee-facing interface |
| Audit | SQLite | Basic decision-path logging |
| Packaging | Docker | Reproducible deployment |

> This fork no longer uses Groq or local HuggingFace embeddings. `app/rag/workflow.py:llm()` and `app/rag/vectorstore.py:get_embeddings()` both read `OPENAI_BASE_URL` / `OPENAI_API_BASE` from `app/core/config.py` and pass it as `openai_api_base` to LangChain.

---

## 6. Project Structure

```text
AgenticAi_project/
│
├── app/
│   ├── api/
│   │   └── routes.py              # Chat, health and ingestion APIs
│   │
│   ├── core/
│   │   ├── config.py              # Environment configuration
│   │   └── logging.py             # Logging configuration
│   │
│   ├── rag/
│   │   ├── state.py               # LangGraph state + structured decisions
│   │   ├── vectorstore.py         # Pinecone + embeddings
│   │   └── workflow.py            # Complete Agentic RAG graph
│   │
│   ├── services/
│   │   ├── audit.py               # SQLite query audit
│   │   └── ingestion.py           # PDF/TXT/MD/DOCX loading + chunking
│   │
│   └── main.py                    # FastAPI application
│
├── data/
│   └── sample_kb/
│       ├── company_it_handbook.md
│       └── service_desk_runbook.md
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
├── templates/
│   └── index.html
│
├── uploads/                   # Uploaded docs (also persisted here)                   # Uploaded docs (also persisted here)
├── .env                         # Local config (not committed, see §7 Step 3)
├── Dockerfile
├── ingest_sample_kb.py
├── requirements.txt              # Pinned, requires Python 3.11 (see §7)
├── run.py                        # Uvicorn entrypoint, port 8080
└── README.md
```

---

## 7. Setup

> Python requirement: **3.11**. `langchain-pinecone==0.2.13` has no wheel for Python 3.14, so create the venv with Python 3.11 (matches `Dockerfile: python:3.11-slim`).

### Step 1 — Create virtual environment (Python 3.11)

```bash
python3.11 -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment

Create a `.env` file in the project root directory (no `.env.example` is shipped). Working config for this AI project:

```env
# OpenAI-compatible endpoint (custom) - must end with /v1
OPENAI_BASE_URL=https://renewably-blog-food.ngrok-free.dev/v1
OPENAI_API_BASE=https://renewably-blog-food.ngrok-free.dev/v1
# From lucy kaggle-nex provider: api_key=ollama
OPENAI_API_KEY=ollama

# External Search
TAVILY_API_KEY=your_tavily_api_key_here

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=fde-it-support-rag
PINECONE_NAMESPACE=company-it-kb

# LLM Models - only model used in this project
OPENAI_MODEL=nex-n2.5-mini
EMBEDDING_MODEL=text-embedding-3-small

# Security - ADMIN_API_KEY protects POST /api/ingest via X-Admin-Key header.
# In prod set this to a long random secret (e.g. openssl rand -hex 32),
# inject via env/secrets manager, never commit it.
ADMIN_API_KEY=change-me-in-production

# Application Settings
APP_ENV=development
```

#### Environment Variable Reference

| Variable | Description | Example | Required |
|---|---|---|---|
| `OPENAI_BASE_URL` / `OPENAI_API_BASE` | OpenAI-compatible base URL, must end with `/v1` | `https://renewably-blog-food.ngrok-free.dev/v1` | ✅ Yes |
| `OPENAI_API_KEY` | Key for custom endpoint (lucy uses `ollama`) | `ollama` | ✅ Yes |
| `TAVILY_API_KEY` | API key for Tavily web search | `tvly-...` | ✅ Yes |
| `PINECONE_API_KEY` | API key for Pinecone vector database | `pckey-...` | ✅ Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | `fde-it-support-rag` | ⚠️ Optional (default: `fde-it-support-rag`) |
| `PINECONE_NAMESPACE` | Pinecone namespace for document isolation | `company-it-kb` | ⚠️ Optional (default: `company-it-kb`) |
| `OPENAI_MODEL` | Only chat model used | `nex-n2.5-mini` | ⚠️ Optional (default: `nex-n2.5-mini`) |
| `EMBEDDING_MODEL` | Embedding model for vectorization (1536 dims) | `text-embedding-3-small` | ⚠️ Optional (default: `text-embedding-3-small`) |
| `ADMIN_API_KEY` | Secret key for admin endpoints (document ingestion). Prod: set random secret, keep out of git, rotate on leak. | `your-secure-key` | ⚠️ Optional (default: `change-me`) |
| `APP_ENV` | Application environment | `development` or `production` | ⚠️ Optional (default: `development`) |

**⚠️ Important Security Notes:**

- Never commit `.env` to version control. Add it to `.gitignore`.
- Change `ADMIN_API_KEY` to a secure random value in production.
- Use environment variables instead of hardcoding secrets.
- Restrict API key access to only the services that need them.

### Step 4 — Load sample company knowledge

```bash
python ingest_sample_kb.py
```

This demonstrates the RAG ingestion pipeline:

```text
Company Documents
   ↓
Load Documents
   ↓
Chunk Text
   ↓
OpenAI-compatible Embeddings (text-embedding-3-small, 1536 dims)
   ↓
Pinecone Vector Database
```

> Note: changing `EMBEDDING_MODEL` changes the vector dimension. `app/rag/vectorstore.py:ensure_index()` deletes and recreates the Pinecone index on dimension mismatch, so re-run ingestion after any embedding-model change.

### Step 5 — Run the application

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8080
```

FastAPI API docs:

```text
http://127.0.0.1:8080/docs
```

---

## 8. Test Cases and Evaluation

### Test A — Private KB Success

Ask:

> **How do I connect to the company VPN from home?**

Expected path:

```text
Router → KB
Private KB Retrieval
KB Grade → GOOD
Generate from Private KB
```

Observation:

> Trusted internal company knowledge is preferred. No public web call is necessary.

---

### Test B — Company Policy Question

Ask:

> **Can IT support ask me to share my MFA code?**

The internal handbook says employees must never share passwords or MFA codes with support personnel.

Expected path:

```text
Router → KB
Private KB Retrieval
KB Grade → GOOD
Private KB Answer
```

Observation:

> RAG allows the model to answer using company-specific information it was never trained on.

---

### Test C — External / Current Information

Ask:

> **What is the latest Microsoft Teams outage guidance?**

Expected path when internal documents do not answer it:

```text
Router → KB
Private KB Retrieval
KB Grade → WEAK
Tavily Search
Web Grade → GOOD
Web Answer
```

Observation:

> Our agent can choose another information source rather than answering from irrelevant vectors.

---

### Test D — Query Rewrite

Ask a deliberately vague question such as:

> **My work communication app is acting strange after the new update. What should I do?**

If both KB and first external retrieval are weak, the workflow can rewrite the query and retry.

Observation:

> Retrieval failure does not mean final failure. Our agent improves the search query and retries, with a retry guard to avoid loops.

---

### Test E — Direct Conversation

Ask:

> **Hello!**

Expected path:

```text
Router → DIRECT
Direct Answer
```

Observation:

> Not every message should trigger vector search or web search.

---

## 9. Document Upload

The sidebar contains **Add Company Document**.

Use the `ADMIN_API_KEY` from `.env`.

Upload one of:

- `.pdf`
- `.txt`
- `.md`
- `.docx`

The backend performs:

```text
Upload
  ↓
Validate Type
  ↓
Load Text
  ↓
Recursive Chunking
  ↓
Embeddings
  ↓
Pinecone Indexing
  ↓
Immediately Available for Retrieval
```

New policies can be added from the UI itself, without editing Python code — any uploaded document is chunked, embedded and indexed, then immediately available for retrieval.

---

## 10. API Endpoints

### `GET /api/health`

Health check.

### `POST /api/chat`

Request:

```json
{
  "question": "How do I reset my company password?"
}
```

Response contains:

```json
{
  "answer": "...",
  "source_used": "private_kb",
  "trace": [
    "Router → KB",
    "Private KB retrieval → 4 chunks",
    "KB evidence grade → GOOD",
    "Answer generation → PRIVATE KB"
  ],
  "citations": []
}
```

### `POST /api/ingest`

Protected by the `X-Admin-Key` request header.

Uploads a document and adds its chunks to Pinecone.

---

