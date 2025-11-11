import csv
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def invoice_status(account_id: str, period: str = None, invoice_id: str = None) -> Dict[str, Any]:
    """
    Retrieve invoice details for an account.
    If period is specified (YYYY-MM), return invoices for that period.
    If invoice_id is specified, return specific invoice.
    Otherwise, return all invoices for the account.
    """
    try:
        csv_path = BASE_DIR / "data" / "invoices.csv"
        if not csv_path.exists():
            return {
                "error": f"invoices.csv not found at {csv_path}",
                "explanation": "CSV file is missing",
                "source": str(csv_path)
            }
        
        invoices = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['account_id'] == account_id:
                    if invoice_id and row['invoice_id'] == invoice_id:
                        return {
                            "invoice_id": row['invoice_id'],
                            "account_id": row['account_id'],
                            "period_start": row['period_start'],
                            "period_end": row['period_end'],
                            "amount": float(row['amount']),
                            "status": row['status'],
                            "issued_on": row['issued_on'],
                            "due_on": row['due_on'],
                            "explanation": f"Invoice {row['invoice_id']} details",
                            "source": f"invoices.csv:{reader.line_num}"
                        }
                    
                    if period:
                        if row['period_start'].startswith(period):
                            invoices.append({
                                "invoice_id": row['invoice_id'],
                                "period_start": row['period_start'],
                                "period_end": row['period_end'],
                                "amount": float(row['amount']),
                                "status": row['status'],
                                "issued_on": row['issued_on'],
                                "due_on": row['due_on']
                            })
                    else:
                        invoices.append({
                            "invoice_id": row['invoice_id'],
                            "period_start": row['period_start'],
                            "period_end": row['period_end'],
                            "amount": float(row['amount']),
                            "status": row['status'],
                            "issued_on": row['issued_on'],
                            "due_on": row['due_on']
                        })
        
        if invoice_id and not invoices:
            return {
                "error": "Invoice not found",
                "explanation": f"No invoice {invoice_id} found for account {account_id}",
                "source": str(csv_path)
            }
        
        summary = {
            "total": sum(inv['amount'] for inv in invoices),
            "paid": sum(inv['amount'] for inv in invoices if inv['status'] == 'Paid'),
            "overdue": sum(inv['amount'] for inv in invoices if inv['status'] == 'Overdue'),
            "pending": sum(inv['amount'] for inv in invoices if inv['status'] == 'Pending')
        }
        
        return {
            "account_id": account_id,
            "invoice_count": len(invoices),
            "invoices": invoices,
            "summary": summary,
            "explanation": f"Found {len(invoices)} invoices for account {account_id}",
            "source": str(csv_path)
        }
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}: {str(e)}",
            "explanation": "Error reading invoices.csv",
            "source": str(csv_path)
        }

