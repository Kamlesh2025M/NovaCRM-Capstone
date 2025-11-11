import csv
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def usage_report(account_id: str, month: str) -> Dict[str, Any]:
    """
    Return API/email/storage usage for a specific month.
    month format: YYYY-MM (e.g., "2025-10")
    Compares usage against plan limits.
    """
    try:
        usage_csv_path = BASE_DIR / "data" / "usage.csv"
        accounts_csv_path = BASE_DIR / "data" / "accounts.csv"
        
        if not usage_csv_path.exists():
            return {
                "error": f"usage.csv not found at {usage_csv_path}",
                "explanation": "CSV file is missing",
                "source": str(usage_csv_path)
            }
        
        usage_data = None
        with open(usage_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['account_id'] == account_id and row['month'] == month:
                    usage_data = {
                        "account_id": row['account_id'],
                        "month": row['month'],
                        "api_calls": int(row['api_calls']),
                        "email_sends": int(row['email_sends']),
                        "storage_gb": float(row['storage_gb'])
                    }
                    break
        
        if not usage_data:
            return {
                "error": "Usage data not found",
                "explanation": f"No usage data found for account {account_id} in month {month}",
                "source": str(usage_csv_path)
            }
        
        plan_limits = {
            "Free": {"api_calls": 10000, "email_sends": 1000, "storage_gb": 5},
            "Pro": {"api_calls": 50000, "email_sends": 10000, "storage_gb": 50},
            "Enterprise": {"api_calls": 500000, "email_sends": 100000, "storage_gb": 500}
        }
        
        plan = "Enterprise"
        if accounts_csv_path.exists():
            with open(accounts_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['account_id'] == account_id:
                        plan = row['plan']
                        break
        
        limits = plan_limits.get(plan, plan_limits["Enterprise"])
        
        usage_data["plan"] = plan
        usage_data["limits"] = limits
        usage_data["usage_percentage"] = {
            "api_calls": round((usage_data["api_calls"] / limits["api_calls"]) * 100, 2),
            "email_sends": round((usage_data["email_sends"] / limits["email_sends"]) * 100, 2),
            "storage_gb": round((usage_data["storage_gb"] / limits["storage_gb"]) * 100, 2)
        }
        
        warnings = []
        if usage_data["usage_percentage"]["api_calls"] > 80:
            warnings.append(f"API calls at {usage_data['usage_percentage']['api_calls']}% of limit")
        if usage_data["usage_percentage"]["email_sends"] > 80:
            warnings.append(f"Email sends at {usage_data['usage_percentage']['email_sends']}% of limit")
        if usage_data["usage_percentage"]["storage_gb"] > 80:
            warnings.append(f"Storage at {usage_data['usage_percentage']['storage_gb']}% of limit")
        
        usage_data["warnings"] = warnings
        usage_data["explanation"] = f"Usage report for {account_id} in {month}"
        usage_data["source"] = f"{usage_csv_path}, {accounts_csv_path}"
        
        return usage_data
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}: {str(e)}",
            "explanation": "Error reading usage or accounts CSV",
            "source": str(usage_csv_path)
        }

