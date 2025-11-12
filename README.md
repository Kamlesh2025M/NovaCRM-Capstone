# NovaCRM Assistant - Customer & Operations Intelligence

A production-ready Agentic AI application that answers customer questions, summarizes account activity, and executes operations tasks by orchestrating Prompt Engineering, LangChain, LangGraph, and MCP (Model Context Protocol).

## Author

Kamlesh Mali - Agentic AI Training Capstone Project

## Overview

NovaCRM Assistant is an intelligent assistant for a fictional B2B SaaS company (NovaCRM) that provides:
- FAQ answering using RAG pipeline over product documentation
- Account data lookup via MCP tools (accounts, invoices, tickets, usage)
- Automatic intent classification and conditional routing
- Conversation memory with checkpointing
- Evidence tracking with citations

## Project Status

**Current Milestone:** M3 - Graph & Routing ✅

### Completed Milestones
- [x] M1 - Data & Docs Setup
- [x] M2 - MCP Server
- [x] M3 - Graph & Routing

### Upcoming Milestones
- [ ] M4 - Prompts & Guardrails
- [ ] M5 - Final Submission

## Current Features

### M1 - Data Organization
- **CSV Datasets**: accounts.csv, invoices.csv, tickets.csv, usage.csv (474 total records)
- **Knowledge Base**: 7 markdown documents covering product docs, pricing, billing, campaigns, support, API, security
- **Build Index Script**: `scripts/build_index.py` - Chunks, embeds, and stores KB in FAISS (~45 chunks)

### M2 - MCP Server
- **5 Production Tools**: account_lookup, invoice_status, ticket_summary, usage_report, kb_search
- **Dual Protocol**: MCP (port 3000) + REST API (port 3001) with Swagger docs

### M3 - Graph & Routing
- **LangGraph State Machine**:
  - 5 nodes: Router, Retrieve, Tools, Synthesize, Escalate
  - Conditional routing based on intent classification (FAQ / DataLookup / Escalation)
  - TypedDict state management with evidence tracking
  
- **RAG Retriever**:
  - FAISS-based semantic search over knowledge base
  - Document formatting with citations
  - Configurable k parameter for result count
  
- **MCP Client Integration**:
  - Synchronous tool calling via REST API
  - Connection testing and error handling
  - Tool parameter determination from query

- **Command-Line Interface**:
  - Interactive and single-query modes
  - Account context management
  - Model/temperature configuration
  - Markdown-formatted output with evidence

- **Prompt Engineering**:
  - System style guide (core principles, banned phrases)
  - Router (few-shot intent classification)
  - RAG synthesis (quality checklist)
  - Tool justification (rationale before calls)

## Setup Instructions (M1)

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd NovaCRM-Capstone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_key_here
   ```

5. **Build FAISS index**
   ```bash
   python scripts/build_index.py
   ```

   This will:
   - Load 7 markdown documents from `data/kb/`
   - Split them into ~45 chunks (500 chars, 50 overlap)
   - Create embeddings using OpenAI
   - Save FAISS index to `index/faiss_index/`

## Project Structure

```
NovaCRM-Capstone/
├── data/                      # CSV datasets and knowledge base
│   ├── accounts.csv           # 50 B2B accounts
│   ├── invoices.csv           # 152 invoices
│   ├── tickets.csv            # 121 support tickets
│   ├── usage.csv              # 152 usage records
│   └── kb/                    # Markdown documentation (7 files)
│       ├── overview.md
│       ├── pricing_plans.md
│       ├── billing_module.md
│       ├── campaigns_module.md
│       ├── support_module.md
│       ├── api_guide.md
│       └── security_faq.md
├── app/                       # Application (M3)
│   ├── __init__.py
│   ├── state.py               # TypedDict state schema
│   ├── retriever.py           # FAISS RAG retriever
│   ├── mcp_client.py          # MCP client (sync)
│   ├── graph.py               # LangGraph state machine (5 nodes)
│   └── cli.py                 # Command-line interface
├── prompts/                   # Prompt templates (M3)
│   ├── system.md              # Style guide
│   ├── router.md              # Intent classification
│   ├── rag_synth.md           # RAG synthesis
│   └── tool_check.md          # Tool justification
├── servers/                   # MCP Server (M2)
│   └── mcp_nova/
│       ├── server.py          # FastMCP server with REST facade
│       └── tools/             # 5 tool implementations
├── index/                     # FAISS vector store (generated, gitignored)
│   └── faiss_index/
├── outputs/                   # Output screenshots and verification
│   ├── M1.jpg                 # M1 milestone output
│   ├── M2.jpg                 # M2 milestone output
│   └── M3.jpg                 # M3 milestone output
├── scripts/                   # Utility scripts
│   └── build_index.py         # Build FAISS index
├── .env.example               # Environment variables template
├── .gitignore                 # Git exclusions
├── requirements.txt           # Python dependencies (M1 + M2 + M3)
├── TEST_MCP_TOOLS.md          # MCP tool testing guide
└── README.md                  # This file
```

## Verification

After completing M1 setup:

1. **Check data files exist:**
   ```bash
   ls data/*.csv
   ls data/kb/*.md
   ```
   You should see 4 CSV files and 7 markdown files.

2. **Verify index was built:**
   ```bash
   ls index/faiss_index/
   ```
   You should see `index.faiss` and `index.pkl` files.

3. **Check for errors:**
   The `build_index.py` script should complete without errors and show:
   ```
   ============================================================
   FAISS Index built successfully!
   Index location: <path>/index/faiss_index
   Total chunks indexed: ~45
   ============================================================
   ```
4. Output from M1

![M1 Output](outputs/M1.jpg)

## Technologies Used

### M1 - Data & RAG
- **Python**: 3.9+
- **LangChain**: 0.3.12
- **FAISS**: 1.9.0 (Vector store for semantic search)
- **OpenAI**: GPT-4o-mini for embeddings

### M2 - MCP Server
- **FastMCP**: 0.4.0 (MCP protocol implementation)
- **FastAPI**: 0.115.6 (REST API framework)
- **Uvicorn**: 0.34.0 (ASGI server)
- **Pydantic**: 2.10.3 (Data validation)

### M3 - Graph & Routing
- **LangGraph**: 0.2.59 (State machine orchestration)
- **LangChain Core**: 0.3.21 (Prompts, output parsers)
- **Requests**: 2.32.3 (HTTP client for MCP)

## M2 - Using MCP Server

### Starting the Server

```bash
# From project root
python servers/mcp_nova/server.py
```

This starts both:
- **MCP Protocol**: http://127.0.0.1:3000
- **REST API**: http://127.0.0.1:3001
- **Swagger Docs**: http://127.0.0.1:3001/docs

### Testing Tools

See `TEST_MCP_TOOLS.md` for comprehensive testing guide.

**Quick Test** (PowerShell):
```powershell
# Test account_lookup
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/account_lookup" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001"}' | ConvertTo-Json

# Test invoice_status
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/invoice_status" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001"}' | ConvertTo-Json
```

**Quick Test** (cURL):
```bash
# Test account_lookup
curl -X POST "http://127.0.0.1:3001/tools/account_lookup" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A001"}'

# Test invoice_status
curl -X POST "http://127.0.0.1:3001/tools/invoice_status" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A001"}'
```

### Tool JSON Contracts

All tools follow consistent contract:

**Success Response**:
```json
{
  "...tool-specific data...",
  "explanation": "Human-readable summary",
  "source": "data source (file:line)"
}
```

**Error Response**:
```json
{
  "error": "Error type: message",
  "explanation": "Human-readable error description",
  "source": "file path"
}
```

### M2 Output

![M2 Output](outputs/M2.jpg)

---

## M3 - Using CLI Assistant

### Prerequisites
1. **FAISS Index**: Must be built first
   ```bash
   python scripts/build_index.py
   ```

2. **MCP Server**: Must be running (for DataLookup queries)
   ```bash
   # Terminal 1
   python servers/mcp_nova/server.py
   ```

### Interactive Mode

```bash
# Terminal 2
python -m app.cli
```

**Features**:
- Continuous conversation
- Account context management (`account A001`)
- Commands: `exit`, `quit`, `q` to end

**Example Session**:
```
You: What is NovaCRM?
[Router] Classified intent: FAQ
[Retrieve] Retrieved 5 documents
...

You: account A001
Account context set to: A001

You: Show my invoices
[Router] Classified intent: DataLookup
[Tools] Called 1 tools
...
```

### Single Query Mode

```bash
# FAQ query
python -m app.cli --query "What are the pricing plans?"

# DataLookup with account context
python -m app.cli --account A001 --query "Show my invoices"

# Custom model and temperature
python -m app.cli --model gpt-4 --temperature 0.3 --query "What is NovaCRM?"
```

### CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--query` | `-q` | None | Single query (omit for interactive) |
| `--account` | `-a` | None | Account ID for context (e.g., A001) |
| `--model` | `-m` | gpt-4o-mini | OpenAI model |
| `--temperature` | `-t` | 0.0 | LLM temperature (0.0-1.0) |

### Output Format

```
================================================================================
NovaCRM Assistant Response
Timestamp: 2025-11-11 12:00:00
Intent: FAQ
================================================================================

## Answer
[Synthesized answer with details]

## Evidence
- doc:pricing_plans.md
- doc:overview.md

================================================================================
```

### Testing Different Intents

**FAQ Queries** (→ Retrieve → Synthesize):
```bash
python -m app.cli -q "What is NovaCRM?"
python -m app.cli -q "How do pricing plans work?"
python -m app.cli -q "What are the API rate limits?"
```

**DataLookup Queries** (→ Tools → Synthesize):
```bash
python -m app.cli -a A001 -q "Show my invoices"
python -m app.cli -a A002 -q "What are my open tickets?"
python -m app.cli -a A003 -q "Check my API usage for October"
```

**Escalation Queries** (→ Escalate):
```bash
python -m app.cli -q "I want to cancel my subscription"
python -m app.cli -q "Request a custom feature"
```

### M3 Output

![M3 Output](outputs/M3.jpg)

---

## Next Steps

After M3 verification and commit:
- **M4**: Add advanced prompts and guardrails
- **M5**: Final integration and submission

## License

This is a capstone project for educational purposes.


