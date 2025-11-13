"""
Comprehensive Test Suite for NovaCRM Graph - M4

Tests all 3 intents (FAQ, DataLookup, Escalation) with validation and guardrails
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.graph import get_graph

def print_result(test_name: str, result: dict):
    """Print test result in a formatted way"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Query: {result['query']}")
    print(f"Intent: {result['intent']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nEvidence ({len(result['evidence'])} items):")
    for e in result['evidence']:
        print(f"  - {e}")
    if result['errors']:
        print(f"\nErrors/Warnings ({len(result['errors'])} items):")
        for err in result['errors']:
            print(f"  - {err}")
    print(f"{'='*80}\n")

def test_faq_queries():
    """Test FAQ intent with various queries"""
    print("\n" + "#"*80)
    print("# FAQ INTENT TESTS")
    print("#"*80)
    
    graph = get_graph()
    
    # Test 1: Simple FAQ
    result = graph.invoke("What is NovaCRM?")
    print_result("FAQ - Product Overview", result)
    assert result['intent'] == "FAQ"
    assert len(result['evidence']) > 0
    assert any("doc:" in e for e in result['evidence'])
    
    # Test 2: Pricing FAQ
    result = graph.invoke("What are the pricing plans for NovaCRM?")
    print_result("FAQ - Pricing Information", result)
    assert result['intent'] == "FAQ"
    
    # Test 3: Technical FAQ
    result = graph.invoke("What are the API rate limits?")
    print_result("FAQ - API Rate Limits", result)
    assert result['intent'] == "FAQ"
    
    # Test 4: Feature FAQ
    result = graph.invoke("How does the contact management feature work?")
    print_result("FAQ - Feature Query", result)
    assert result['intent'] == "FAQ"
    
    print("\n✅ FAQ Tests Complete\n")

def test_datalookup_queries():
    """Test DataLookup intent with various queries"""
    print("\n" + "#"*80)
    print("# DATA LOOKUP INTENT TESTS")
    print("#"*80)
    
    graph = get_graph()
    
    # Test 1: Account lookup
    result = graph.invoke("What is the plan for account A001?", account_context="A001")
    print_result("DataLookup - Account Info", result)
    assert result['intent'] == "DataLookup"
    assert any("tool:" in e for e in result['evidence'])
    
    # Test 2: Invoice status
    result = graph.invoke("Show me invoices for A002 in October 2025", account_context="A002")
    print_result("DataLookup - Invoice Query", result)
    assert result['intent'] == "DataLookup"
    
    # Test 3: Ticket summary
    result = graph.invoke("How many open tickets does Company_005 have?")
    print_result("DataLookup - Ticket Summary", result)
    assert result['intent'] == "DataLookup"
    
    # Test 4: Usage report
    result = graph.invoke("What is my API usage for A003 in November 2025?", account_context="A003")
    print_result("DataLookup - Usage Report", result)
    assert result['intent'] == "DataLookup"
    
    print("\n✅ DataLookup Tests Complete\n")

def test_escalation_queries():
    """Test Escalation intent with various queries"""
    print("\n" + "#"*80)
    print("# ESCALATION INTENT TESTS")
    print("#"*80)
    
    graph = get_graph()
    
    # Test 1: Account termination
    result = graph.invoke("I want to cancel my subscription")
    print_result("Escalation - Account Termination", result)
    assert result['intent'] == "Escalation"
    assert "support" in result['answer'].lower() or "contact" in result['answer'].lower()
    
    # Test 2: Billing dispute
    result = graph.invoke("There's an unauthorized charge on my account, I need a refund")
    print_result("Escalation - Billing Dispute", result)
    assert result['intent'] == "Escalation"
    
    # Test 3: Legal matter
    result = graph.invoke("I need to discuss a legal matter with your team")
    print_result("Escalation - Legal Issue", result)
    assert result['intent'] == "Escalation"
    
    # Test 4: Ambiguous query
    result = graph.invoke("Help me with something")
    print_result("Escalation - Ambiguous Query", result)
    assert result['intent'] == "Escalation"
    
    print("\n✅ Escalation Tests Complete\n")

def test_safety_guardrails():
    """Test safety and validation features"""
    print("\n" + "#"*80)
    print("# SAFETY & VALIDATION TESTS")
    print("#"*80)
    
    graph = get_graph()
    
    # Test 1: PII in query
    result = graph.invoke("My email is john.doe@example.com and I need help")
    print_result("Safety - PII Redaction", result)
    assert any("safety:pii_redacted" in e for e in result['evidence'])
    
    # Test 2: Sensitive topic
    result = graph.invoke("I think my account was breached")
    print_result("Safety - Data Breach Detection", result)
    assert result['intent'] == "Escalation"
    
    # Test 3: Invalid account ID format (should still work but log warning)
    result = graph.invoke("Show me info for account XYZ123")
    print_result("Safety - Invalid Account Format", result)
    # Should escalate or handle gracefully
    
    print("\n✅ Safety & Validation Tests Complete\n")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "#"*80)
    print("# EDGE CASE TESTS")
    print("#"*80)
    
    graph = get_graph()
    
    # Test 1: Empty query (should be handled gracefully)
    try:
        result = graph.invoke("")
        print_result("Edge Case - Empty Query", result)
    except Exception as e:
        print(f"Edge Case - Empty Query: Caught exception (expected): {e}")
    
    # Test 2: Very long query
    long_query = "What is NovaCRM? " * 100
    result = graph.invoke(long_query)
    print_result("Edge Case - Long Query", result)
    
    # Test 3: Special characters
    result = graph.invoke("What is <NovaCRM>?")
    print_result("Edge Case - Special Characters", result)
    
    # Test 4: Mixed intent query
    result = graph.invoke("What is NovaCRM pricing and show me my invoices for A001?", account_context="A001")
    print_result("Edge Case - Mixed Intent", result)
    # Should classify to one intent (likely DataLookup since it has specific account request)
    
    print("\n✅ Edge Case Tests Complete\n")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print(" " * 20 + "NovaCRM GRAPH - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    try:
        test_faq_queries()
        test_datalookup_queries()
        test_escalation_queries()
        test_safety_guardrails()
        test_edge_cases()
        
        print("\n" + "="*80)
        print(" " * 30 + "ALL TESTS PASSED ✅")
        print("=" * 80 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    run_all_tests()

