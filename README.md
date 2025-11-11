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

**Current Milestone:** M2 - MCP Server ✅

### Completed Milestones
- [x] M1 - Data & Docs Setup
- [x] M2 - MCP Server

### Upcoming Milestones
- [ ] M3 - Graph & Routing
- [ ] M4 - Prompts & Guardrails
- [ ] M5 - Final Submission

## Current Features

### M1 - Data Organization
- **CSV Datasets**: accounts.csv, invoices.csv, tickets.csv, usage.csv (474 total records)
- **Knowledge Base**: 7 markdown documents covering product docs, pricing, billing, campaigns, support, API, security
- **Build Index Script**: `scripts/build_index.py` - Chunks, embeds, and stores KB in FAISS (~45 chunks)

### M2 - MCP Server
- **5 Production Tools**:
  1. `account_lookup` - Get account details by ID or company name
  2. `invoice_status` - Retrieve invoices and payment status (with period filtering)
  3. `ticket_summary` - Get open tickets and SLA risks (with time window)
  4. `usage_report` - API/email/storage usage vs plan limits (with warnings)
  5. `kb_search` - Search knowledge base documents (keyword-based fallback)

- **Dual Protocol Support**:
  - MCP Protocol on port 3000 (for MCP clients)
  - REST API on port 3001 (for HTTP access)
  - Swagger documentation at /docs

- **Robust Design**:
  - All tools return JSON with `explanation` and `source` fields
  - Graceful error handling with descriptive messages
  - Thread-safe operation with concurrent MCP and REST servers

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
├── servers/                   # MCP Server (M2)
│   └── mcp_nova/
│       ├── server.py          # FastMCP server with REST facade
│       └── tools/             # Tool implementations
│           ├── __init__.py
│           ├── account.py     # account_lookup tool
│           ├── invoice.py     # invoice_status tool
│           ├── ticket.py      # ticket_summary tool
│           ├── usage.py       # usage_report tool
│           └── kb_search.py   # kb_search tool
├── index/                     # FAISS vector store (generated, gitignored)
│   └── faiss_index/
├── scripts/                   # Utility scripts
│   └── build_index.py         # Build FAISS index
├── .env.example               # Environment variables template
├── .gitignore                 # Git exclusions
├── requirements.txt           # Python dependencies (M1 + M2)
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

---

## Next Steps

After M2 verification and commit:
- **M3**: Build LangGraph state machine with conditional routing
- **M4**: Add prompt templates and guardrails
- **M5**: Integrate CLI/API and final submission

## License

This is a capstone project for educational purposes.


