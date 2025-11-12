# M2 - MCP Server Tool Testing

This document provides example calls for testing all 5 MCP tools.

## Setup

1. **Start the MCP Server**
   ```bash
   python servers/mcp_nova/server.py
   ```

2. **Access Points**
   - MCP Protocol: http://127.0.0.1:3000
   - REST API: http://127.0.0.1:3001
   - Swagger Docs: http://127.0.0.1:3001/docs

---

## Tool 1: account_lookup

**Purpose**: Look up account details by account_id or company name

**Test with cURL (Windows PowerShell)**:
```powershell
# By account_id
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/account_lookup" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001"}' | ConvertTo-Json

# By company name
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/account_lookup" `
  -ContentType "application/json" `
  -Body '{"company": "Company_001"}' | ConvertTo-Json
```

**Test with cURL (Linux/Mac)**:
```bash
# By account_id
curl -X POST "http://127.0.0.1:3001/tools/account_lookup" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A001"}'

# By company name
curl -X POST "http://127.0.0.1:3001/tools/account_lookup" \
  -H "Content-Type: application/json" \
  -d '{"company": "Company_001"}'
```

**Expected Response**:
```json
{
  "account_id": "A001",
  "company": "Company_001",
  "plan": "Enterprise",
  "tier": "Premium",
  "billing_cycle": "Annual",
  "csm": "Alice Thompson",
  "renewal_date": "2025-03-15",
  "explanation": "Account details for Company_001",
  "source": "accounts.csv:2"
}
```

---

## Tool 2: invoice_status

**Purpose**: Retrieve invoice details and payment status for an account

**Test with PowerShell**:
```powershell
# All invoices for account
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/invoice_status" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001"}' | ConvertTo-Json

# Invoices for specific period
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/invoice_status" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001", "period": "2025-10"}' | ConvertTo-Json

# Specific invoice
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/invoice_status" `
  -ContentType "application/json" `
  -Body '{"account_id": "A001", "invoice_id": "INV-A001-2025-10"}' | ConvertTo-Json
```

**Test with cURL**:
```bash
# All invoices for account
curl -X POST "http://127.0.0.1:3001/tools/invoice_status" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A001"}'

# Invoices for specific period
curl -X POST "http://127.0.0.1:3001/tools/invoice_status" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A001", "period": "2025-10"}'
```

**Expected Response**:
```json
{
  "account_id": "A001",
  "invoice_count": 3,
  "invoices": [
    {
      "invoice_id": "INV-A001-2025-10",
      "period_start": "2025-10-01",
      "period_end": "2025-10-31",
      "amount": 799.0,
      "status": "Paid",
      "issued_on": "2025-10-01",
      "due_on": "2025-10-15"
    }
  ],
  "summary": {
    "total": 2397.0,
    "paid": 2397.0,
    "overdue": 0,
    "pending": 0
  },
  "explanation": "Found 3 invoices for account A001",
  "source": "invoices.csv"
}
```

---

## Tool 3: ticket_summary

**Purpose**: Get summary of open tickets and SLA risks

**Test with PowerShell**:
```powershell
# Default window (90 days)
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/ticket_summary" `
  -ContentType "application/json" `
  -Body '{"account_id": "A002"}' | ConvertTo-Json

# Custom window (30 days)
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/ticket_summary" `
  -ContentType "application/json" `
  -Body '{"account_id": "A002", "window_days": 30}' | ConvertTo-Json
```

**Test with cURL**:
```bash
# Default window (90 days)
curl -X POST "http://127.0.0.1:3001/tools/ticket_summary" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A002"}'

# Custom window (30 days)
curl -X POST "http://127.0.0.1:3001/tools/ticket_summary" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A002", "window_days": 30}'
```

**Expected Response**:
```json
{
  "account_id": "A002",
  "window_days": 90,
  "total_tickets": 5,
  "open_tickets": 2,
  "high_priority_open": 1,
  "status_breakdown": {
    "Open": 2,
    "Closed": 3
  },
  "priority_breakdown": {
    "High": 1,
    "Medium": 3,
    "Low": 1
  },
  "sla_risks": [
    {
      "ticket_id": "T-A002-001",
      "subject": "Integration Issue",
      "days_open": 12,
      "priority": "High"
    }
  ],
  "open_ticket_details": [...],
  "explanation": "Found 5 tickets in last 90 days, 2 open",
  "source": "tickets.csv"
}
```

---

## Tool 4: usage_report

**Purpose**: Get API/email/storage usage metrics vs plan limits

**Test with PowerShell**:
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/usage_report" `
  -ContentType "application/json" `
  -Body '{"account_id": "A003", "month": "2025-10"}' | ConvertTo-Json
```

**Test with cURL**:
```bash
curl -X POST "http://127.0.0.1:3001/tools/usage_report" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "A003", "month": "2025-10"}'
```

**Expected Response**:
```json
{
  "account_id": "A003",
  "month": "2025-10",
  "api_calls": 28500,
  "email_sends": 7800,
  "storage_gb": 38.5,
  "plan": "Pro",
  "limits": {
    "api_calls": 50000,
    "email_sends": 10000,
    "storage_gb": 50
  },
  "usage_percentage": {
    "api_calls": 57.0,
    "email_sends": 78.0,
    "storage_gb": 77.0
  },
  "warnings": [],
  "explanation": "Usage report for A003 in 2025-10",
  "source": "usage.csv, accounts.csv"
}
```

---

## Tool 5: kb_search

**Purpose**: Search knowledge base documents (fallback keyword search)

**Test with PowerShell**:
```powershell
# Search for "pricing"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/kb_search" `
  -ContentType "application/json" `
  -Body '{"query": "pricing", "k": 3}' | ConvertTo-Json

# Search for "API"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3001/tools/kb_search" `
  -ContentType "application/json" `
  -Body '{"query": "API", "k": 5}' | ConvertTo-Json
```

**Test with cURL**:
```bash
# Search for "pricing"
curl -X POST "http://127.0.0.1:3001/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "pricing", "k": 3}'

# Search for "API"
curl -X POST "http://127.0.0.1:3001/tools/kb_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "API", "k": 5}'
```

**Expected Response**:
```json
{
  "query": "pricing",
  "results_count": 2,
  "results": [
    {
      "document": "pricing_plans.md",
      "content": "# NovaCRM Pricing Plans\n\nNovaCRM offers three pricing tiers...",
      "matches": [
        "# NovaCRM Pricing Plans",
        "Our pricing is designed to scale with your business..."
      ]
    },
    {
      "document": "billing_module.md",
      "content": "# Billing Module\n\nManage subscriptions and pricing...",
      "matches": [
        "Manage subscriptions and pricing configuration..."
      ]
    }
  ],
  "explanation": "Found 2 documents matching 'pricing'",
  "source": "data/kb"
}
```

---

## Verification Checklist

Test each tool and verify:

- [ ] **account_lookup** returns account details correctly
- [ ] **account_lookup** handles missing accounts gracefully
- [ ] **invoice_status** returns all invoices for an account
- [ ] **invoice_status** filters by period correctly
- [ ] **invoice_status** returns correct summary (total, paid, overdue)
- [ ] **ticket_summary** counts open tickets accurately
- [ ] **ticket_summary** identifies SLA risks (high priority > 7 days)
- [ ] **usage_report** calculates usage percentages correctly
- [ ] **usage_report** warns when usage > 80%
- [ ] **kb_search** finds relevant documents
- [ ] All tools return `explanation` and `source` fields
- [ ] All tools handle errors gracefully (missing files, invalid inputs)

---

## Swagger UI Testing

For interactive testing, visit: http://127.0.0.1:3001/docs

The Swagger UI provides:
- Interactive API documentation
- Try-it-out functionality for each endpoint
- Request/response schemas
- Example values

---

## JSON Contracts

All tools follow the same contract pattern:

### Success Response
```json
{
  "...tool-specific data...",
  "explanation": "Human-readable summary",
  "source": "data source (file:line)"
}
```

### Error Response
```json
{
  "error": "Error type: Error message",
  "explanation": "Human-readable error description",
  "source": "file path where error occurred"
}
```

---

## Common Test Scenarios

### Test Account IDs
- A001, A002, A003, A004, A005 (various plans and tiers)

### Test Periods
- 2025-10, 2025-09, 2025-08 (recent months with data)

### Test Company Names
- Company_001, Company_002, Company_005

---

## Next Steps (M3)

After verifying M2 tools work correctly:
- Commit M2 to git
- Proceed to M3 - Graph & Routing (LangGraph implementation)

