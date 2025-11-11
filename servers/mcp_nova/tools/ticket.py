import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def ticket_summary(account_id: str, window_days: int = 90) -> Dict[str, Any]:
    """
    Return summary of open tickets and SLA risks for an account.
    window_days: number of days to look back (default 90)
    """
    try:
        csv_path = BASE_DIR / "data" / "tickets.csv"
        if not csv_path.exists():
            return {
                "error": f"tickets.csv not found at {csv_path}",
                "explanation": "CSV file is missing",
                "source": str(csv_path)
            }
        
        cutoff_date = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
        
        tickets = []
        open_tickets = []
        high_priority_open = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['account_id'] == account_id and row['opened_on'] >= cutoff_date:
                    ticket_data = {
                        "ticket_id": row['ticket_id'],
                        "opened_on": row['opened_on'],
                        "priority": row['priority'],
                        "status": row['status'],
                        "subject": row['subject'],
                        "owner": row['owner']
                    }
                    tickets.append(ticket_data)
                    
                    if row['status'] in ['Open', 'Pending']:
                        open_tickets.append(ticket_data)
                        
                        if row['priority'] == 'High':
                            high_priority_open.append(ticket_data)
        
        status_counts = {}
        priority_counts = {}
        for ticket in tickets:
            status = ticket['status']
            priority = ticket['priority']
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        sla_risks = []
        for ticket in high_priority_open:
            opened = datetime.strptime(ticket['opened_on'], '%Y-%m-%d')
            days_open = (datetime.now() - opened).days
            if days_open > 7:
                sla_risks.append({
                    "ticket_id": ticket['ticket_id'],
                    "subject": ticket['subject'],
                    "days_open": days_open,
                    "priority": ticket['priority']
                })
        
        return {
            "account_id": account_id,
            "window_days": window_days,
            "total_tickets": len(tickets),
            "open_tickets": len(open_tickets),
            "high_priority_open": len(high_priority_open),
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "sla_risks": sla_risks,
            "open_ticket_details": open_tickets,
            "explanation": f"Found {len(tickets)} tickets in last {window_days} days, {len(open_tickets)} open",
            "source": str(csv_path)
        }
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}: {str(e)}",
            "explanation": "Error reading tickets.csv",
            "source": str(csv_path)
        }

