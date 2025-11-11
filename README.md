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

**Current Milestone:** M1 - Data & Docs Setup ✅

### Completed Milestones
- [x] M1 - Data & Docs Setup

### Upcoming Milestones
- [ ] M2 - MCP Server
- [ ] M3 - Graph & Routing
- [ ] M4 - Prompts & Guardrails
- [ ] M5 - Final Submission

## Current Features (M1)

### Data Organization
- **CSV Datasets**: accounts.csv, invoices.csv, tickets.csv, usage.csv
- **Knowledge Base**: 7 markdown documents covering:
  - Product overview
  - Pricing plans
  - Billing module
  - Campaigns module
  - Support module
  - API guide
  - Security FAQ

### Build Index Script
- `scripts/build_index.py` - Chunks, embeds, and stores knowledge base in FAISS

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
│   ├── accounts.csv
│   ├── invoices.csv
│   ├── tickets.csv
│   ├── usage.csv
│   └── kb/                    # Markdown documentation
│       ├── overview.md
│       ├── pricing_plans.md
│       ├── billing_module.md
│       ├── campaigns_module.md
│       ├── support_module.md
│       ├── api_guide.md
│       └── security_faq.md
├── index/                     # FAISS vector store (generated)
│   └── faiss_index/
├── scripts/                   # Utility scripts
│   └── build_index.py        # Build FAISS index
├── .env.example              # Environment variables template
├── .gitignore               # Git exclusions
├── requirements.txt         # Python dependencies
└── README.md               # This file
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

- **Python**: 3.9+
- **LangChain**: 0.3.12
- **FAISS**: 1.9.0 (Vector store for semantic search)
- **OpenAI**: GPT-4o-mini for embeddings

## Next Steps

Once M1 is complete and committed:
- **M2**: Implement MCP server with 4+ tools
- **M3**: Build LangGraph state machine with routing
- **M4**: Add prompt templates and guardrails
- **M5**: Integrate CLI/API and final submission

## License

This is a capstone project for educational purposes.


