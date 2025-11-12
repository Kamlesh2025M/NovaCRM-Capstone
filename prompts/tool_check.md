# Tool Justification Prompt

Before calling MCP tools, you must provide a brief rationale.

## Purpose

This step ensures:
1. Tool calls are necessary and appropriate
2. Correct tools are selected for the query
3. Required parameters are available
4. User understands what data will be accessed

## Justification Format

For each tool you plan to call, state:

```
Tool: [tool_name]
Reason: [One line explaining why this tool is needed]
Parameters: [List of parameters and their values]
Expected Output: [What information this will provide]
```

## Tool Reference

### account_lookup
- **Use when**: Need account details, plan info, CSM, renewal dates
- **Parameters**: account_id OR company (at least one required)
- **Returns**: Plan, tier, billing cycle, CSM, renewal date

### invoice_status
- **Use when**: Need invoice details, payment status, billing history
- **Parameters**: account_id (required), period (optional), invoice_id (optional)
- **Returns**: Invoice list, payment status, amounts, summary

### ticket_summary
- **Use when**: Need support ticket status, SLA risks, ticket counts
- **Parameters**: account_id (required), window_days (optional, default 90)
- **Returns**: Open tickets, priority breakdown, SLA risks

### usage_report
- **Use when**: Need API/email/storage usage metrics
- **Parameters**: account_id (required), month in YYYY-MM format (required)
- **Returns**: Usage vs limits, percentages, warnings

### kb_search
- **Use when**: Need to search documentation (fallback if FAISS fails)
- **Parameters**: query (required), k (optional, default 5)
- **Returns**: Matching documents and content

## Validation Rules

Before proceeding:
1. Verify you have all required parameters
2. Confirm account_id format (should be like A001, A002, etc.)
3. Check month format is YYYY-MM
4. Ensure query intent matches tool capability

## Example

Query: "What's the invoice status for Company_003 in October 2025?"

Justification:
```
Tool: account_lookup
Reason: Need to find account_id for Company_003
Parameters: company="Company_003"
Expected Output: Account ID and basic details

Tool: invoice_status
Reason: Retrieve invoice data for October 2025
Parameters: account_id=[from previous call], period="2025-10"
Expected Output: Invoice details, payment status, amounts
```

## Now justify your tool calls for this query:

Query: {query}
Account Context: {account_context}

Justification:

