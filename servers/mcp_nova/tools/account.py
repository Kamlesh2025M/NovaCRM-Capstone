import csv
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def account_lookup(account_id: str = None, company: str = None) -> Dict[str, Any]:
    """
    Look up account details by account_id or company name.
    Returns plan, tier, renewal date, CSM, and flags.
    """
    try:
        csv_path = BASE_DIR / "data" / "accounts.csv"
        if not csv_path.exists():
            return {
                "error": f"accounts.csv not found at {csv_path}",
                "explanation": "CSV file is missing",
                "source": str(csv_path)
            }
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (account_id and row['account_id'] == account_id) or \
                   (company and row['company'].lower() == company.lower()):
                    return {
                        "account_id": row['account_id'],
                        "company": row['company'],
                        "plan": row['plan'],
                        "tier": row['tier'],
                        "billing_cycle": row['billing_cycle'],
                        "csm": row['csm'],
                        "renewal_date": row['renewal_date'],
                        "explanation": f"Account details for {row['company']}",
                        "source": f"accounts.csv:{reader.line_num}"
                    }
        
        return {
            "error": "Account not found",
            "explanation": f"No account found for account_id={account_id}, company={company}",
            "source": str(csv_path)
        }
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}: {str(e)}",
            "explanation": "Error reading accounts.csv",
            "source": str(csv_path)
        }

