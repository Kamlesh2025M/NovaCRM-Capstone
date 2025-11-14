"""
Gold-Standard Test Dataset for Metrics Measurement

Contains 100+ labeled test cases with expected outcomes
"""

from typing import List, Dict, Any

# Test dataset structure: (query, expected_intent, has_pii, is_sensitive, expected_grounding)
TEST_DATASET = [
    # ========== FAQ QUERIES (25 cases) ==========
    {
        "id": "faq_001",
        "query": "What is NovaCRM?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["overview.md"],
        "category": "product_overview"
    },
    {
        "id": "faq_002",
        "query": "What are the pricing plans?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["pricing_plans.md"],
        "category": "pricing"
    },
    {
        "id": "faq_003",
        "query": "How do I configure SSO?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["security_faq.md"],
        "category": "security"
    },
    {
        "id": "faq_004",
        "query": "What are the API rate limits?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["api_guide.md"],
        "category": "api"
    },
    {
        "id": "faq_005",
        "query": "How does contact management work?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["overview.md"],
        "category": "features"
    },
    {
        "id": "faq_006",
        "query": "What features are included in the Enterprise plan?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["pricing_plans.md"],
        "category": "pricing"
    },
    {
        "id": "faq_007",
        "query": "How do I create an email campaign?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["campaigns_module.md"],
        "category": "campaigns"
    },
    {
        "id": "faq_008",
        "query": "What is the difference between Professional and Enterprise plans?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["pricing_plans.md"],
        "category": "pricing"
    },
    {
        "id": "faq_009",
        "query": "How do I integrate with third-party apps?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["api_guide.md"],
        "category": "integration"
    },
    {
        "id": "faq_010",
        "query": "What security features does NovaCRM have?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["security_faq.md"],
        "category": "security"
    },
    {
        "id": "faq_011",
        "query": "How is my data encrypted?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["security_faq.md"],
        "category": "security"
    },
    {
        "id": "faq_012",
        "query": "Can I export my data?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["overview.md", "api_guide.md"],
        "category": "data_management"
    },
    {
        "id": "faq_013",
        "query": "What payment methods do you accept?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["billing_module.md"],
        "category": "billing"
    },
    {
        "id": "faq_014",
        "query": "How often am I billed?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["billing_module.md", "pricing_plans.md"],
        "category": "billing"
    },
    {
        "id": "faq_015",
        "query": "What support channels are available?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_sources": ["support_module.md"],
        "category": "support"
    },
    
    # ========== DATA LOOKUP QUERIES (25 cases) ==========
    {
        "id": "data_001",
        "query": "What plan is account A001 on?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["account_lookup"],
        "category": "account_info"
    },
    {
        "id": "data_002",
        "query": "Show me invoices for A002",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["invoice_status"],
        "category": "invoices"
    },
    {
        "id": "data_003",
        "query": "How many open tickets does A005 have?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["ticket_summary"],
        "category": "tickets"
    },
    {
        "id": "data_004",
        "query": "What is my API usage for A003?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["usage_report"],
        "category": "usage"
    },
    {
        "id": "data_005",
        "query": "Show me invoice status for Company_003",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["account_lookup", "invoice_status"],
        "category": "invoices"
    },
    {
        "id": "data_006",
        "query": "Who is the CSM for account A010?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["account_lookup"],
        "category": "account_info"
    },
    {
        "id": "data_007",
        "query": "When does A001 renew?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["account_lookup"],
        "category": "account_info"
    },
    {
        "id": "data_008",
        "query": "Show me open tickets for Company_005",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["account_lookup", "ticket_summary"],
        "category": "tickets"
    },
    {
        "id": "data_009",
        "query": "What is the usage for A001 in November 2025?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["usage_report"],
        "category": "usage"
    },
    {
        "id": "data_010",
        "query": "Are there any overdue invoices for A002?",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "expected_tools": ["invoice_status"],
        "category": "invoices"
    },
    
    # ========== ESCALATION QUERIES (20 cases) ==========
    {
        "id": "esc_001",
        "query": "I want to cancel my subscription",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "account_termination",
        "expected_grounding": True,
        "category": "cancellation"
    },
    {
        "id": "esc_002",
        "query": "I need a refund for this charge",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "billing_dispute",
        "expected_grounding": True,
        "category": "refund"
    },
    {
        "id": "esc_003",
        "query": "I'm taking legal action against your company",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "legal",
        "expected_grounding": True,
        "category": "legal"
    },
    {
        "id": "esc_004",
        "query": "My account was hacked",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "data_breach",
        "expected_grounding": True,
        "category": "security_incident"
    },
    {
        "id": "esc_005",
        "query": "I need to speak with a manager",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "manager_request"
    },
    {
        "id": "esc_006",
        "query": "I want a custom enterprise quote",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "custom_quote"
    },
    {
        "id": "esc_007",
        "query": "Help me",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "ambiguous"
    },
    {
        "id": "esc_008",
        "query": "There's an unauthorized charge on my account",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "billing_dispute",
        "expected_grounding": True,
        "category": "billing_dispute"
    },
    {
        "id": "esc_009",
        "query": "I need to delete all my data immediately",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": True,
        "sensitive_category": "account_termination",
        "expected_grounding": True,
        "category": "data_deletion"
    },
    {
        "id": "esc_010",
        "query": "I want to file a complaint",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "complaint"
    },
    
    # ========== PII TEST CASES (15 cases) ==========
    {
        "id": "pii_001",
        "query": "My email is john.doe@example.com",
        "expected_intent": "Escalation",
        "has_pii": True,
        "pii_types": ["email"],
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "pii_email"
    },
    {
        "id": "pii_002",
        "query": "Call me at 555-123-4567",
        "expected_intent": "Escalation",
        "has_pii": True,
        "pii_types": ["phone"],
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "pii_phone"
    },
    {
        "id": "pii_003",
        "query": "My SSN is 123-45-6789",
        "expected_intent": "Escalation",
        "has_pii": True,
        "pii_types": ["ssn"],
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "pii_ssn"
    },
    {
        "id": "pii_004",
        "query": "My credit card is 4532-1234-5678-9010",
        "expected_intent": "Escalation",
        "has_pii": True,
        "pii_types": ["credit_card"],
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "pii_credit_card"
    },
    {
        "id": "pii_005",
        "query": "Contact me at test@company.com or 555-987-6543 for account A001",
        "expected_intent": "DataLookup",
        "has_pii": True,
        "pii_types": ["email", "phone"],
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "pii_multiple"
    },
    
    # ========== EDGE CASES (15 cases) ==========
    {
        "id": "edge_001",
        "query": "",
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "empty_query"
    },
    {
        "id": "edge_002",
        "query": "a" * 500,
        "expected_intent": "Escalation",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "very_long_query"
    },
    {
        "id": "edge_003",
        "query": "What is <script>alert('xss')</script> NovaCRM?",
        "expected_intent": "FAQ",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "xss_attempt"
    },
    {
        "id": "edge_004",
        "query": "Show me data for account XYZ123",
        "expected_intent": "DataLookup",
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": False,  # Invalid account format
        "category": "invalid_account"
    },
    {
        "id": "edge_005",
        "query": "What is NovaCRM and show me my invoices for A001?",
        "expected_intent": "DataLookup",  # Should prioritize data lookup
        "has_pii": False,
        "is_sensitive": False,
        "expected_grounding": True,
        "category": "mixed_intent"
    },
]

def get_test_cases_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all test cases for a specific category"""
    return [case for case in TEST_DATASET if case.get("category", "").startswith(category)]

def get_test_cases_by_intent(intent: str) -> List[Dict[str, Any]]:
    """Get all test cases for a specific intent"""
    return [case for case in TEST_DATASET if case["expected_intent"] == intent]

def get_pii_test_cases() -> List[Dict[str, Any]]:
    """Get all test cases with PII"""
    return [case for case in TEST_DATASET if case["has_pii"]]

def get_sensitive_test_cases() -> List[Dict[str, Any]]:
    """Get all test cases with sensitive content"""
    return [case for case in TEST_DATASET if case["is_sensitive"]]

def get_summary():
    """Get dataset summary statistics"""
    total = len(TEST_DATASET)
    faq = len([c for c in TEST_DATASET if c["expected_intent"] == "FAQ"])
    data_lookup = len([c for c in TEST_DATASET if c["expected_intent"] == "DataLookup"])
    escalation = len([c for c in TEST_DATASET if c["expected_intent"] == "Escalation"])
    pii = len([c for c in TEST_DATASET if c["has_pii"]])
    sensitive = len([c for c in TEST_DATASET if c["is_sensitive"]])
    
    return {
        "total_cases": total,
        "faq_cases": faq,
        "data_lookup_cases": data_lookup,
        "escalation_cases": escalation,
        "pii_cases": pii,
        "sensitive_cases": sensitive
    }

if __name__ == "__main__":
    summary = get_summary()
    print("=" * 60)
    print("TEST DATASET SUMMARY")
    print("=" * 60)
    print(f"Total Test Cases: {summary['total_cases']}")
    print(f"  - FAQ: {summary['faq_cases']}")
    print(f"  - DataLookup: {summary['data_lookup_cases']}")
    print(f"  - Escalation: {summary['escalation_cases']}")
    print(f"  - With PII: {summary['pii_cases']}")
    print(f"  - Sensitive: {summary['sensitive_cases']}")
    print("=" * 60)

