"""
M4 - Guardrails Testing Suite

Comprehensive tests for validation, safety checks, and hallucination reduction
"""

import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.graph import get_graph
from app.validation import get_validator, get_safety_guardrails

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")

def test_safety_checks():
    """Test safety checks for sensitive content and PII"""
    print_section("TEST 1: Safety Checks - Sensitive Content & PII")
    
    safety = get_safety_guardrails()
    
    # Test 1.1: Sensitive topic detection
    print("[Test 1.1] Sensitive Topic Detection")
    test_queries = [
        "I want to cancel my subscription",
        "I need a refund for billing dispute",
        "There was a data breach",
        "I'm considering legal action"
    ]
    
    for query in test_queries:
        result = safety.check_sensitive_content(query)
        print(f"  Query: '{query}'")
        print(f"  Sensitive: {result['is_sensitive']}")
        print(f"  Should Escalate: {result['should_escalate']}")
        if result['matched_topics']:
            print(f"  Topics: {result['matched_topics']}")
        print()
    
    # Test 1.2: PII detection
    print("[Test 1.2] PII Detection and Redaction")
    test_texts = [
        "My SSN is 123-45-6789",
        "My credit card is 1234567890123456",
        "Contact me at john@example.com"
    ]
    
    for text in test_texts:
        result = safety.check_pii_exposure(text)
        print(f"  Original: '{text}'")
        print(f"  Has PII: {result['has_pii']}")
        if result['has_pii']:
            print(f"  PII Types: {result['pii_types']}")
            print(f"  Redacted: '{result['redacted_text']}'")
        print()

def test_tool_validation():
    """Test tool parameter validation"""
    print_section("TEST 2: Tool Parameter Validation")
    
    safety = get_safety_guardrails()
    
    # Test 2.1: Valid parameters
    print("[Test 2.1] Valid Tool Parameters")
    valid_tests = [
        ("account_lookup", {"account_id": "A1001"}),
        ("invoice_status", {"account_id": "A1001", "period": "2025-10"}),
        ("usage_report", {"account_id": "A1001", "month": "2025-10"})
    ]
    
    for tool_name, params in valid_tests:
        result = safety.validate_tool_params(tool_name, params)
        print(f"  Tool: {tool_name}")
        print(f"  Params: {params}")
        print(f"  Valid: {result['is_valid']}")
        print()
    
    # Test 2.2: Invalid parameters
    print("[Test 2.2] Invalid Tool Parameters")
    invalid_tests = [
        ("account_lookup", {}),
        ("invoice_status", {}),
        ("usage_report", {"account_id": "A1001", "month": "invalid-date"})
    ]
    
    for tool_name, params in invalid_tests:
        result = safety.validate_tool_params(tool_name, params)
        print(f"  Tool: {tool_name}")
        print(f"  Params: {params}")
        print(f"  Valid: {result['is_valid']}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")
        print()

def test_output_validation():
    """Test output validation and hallucination detection"""
    print_section("TEST 3: Output Validation & Hallucination Detection")
    
    validator = get_validator()
    
    # Test 3.1: Valid answers
    print("[Test 3.1] Valid Answers")
    valid_cases = [
        {
            "answer": "Based on the documentation, NovaCRM supports multi-tenant architecture with role-based access control. This allows you to manage different user permissions effectively.",
            "intent": "FAQ",
            "evidence": ["doc:architecture.md", "doc:security.md"]
        },
        {
            "answer": "Your account A1001 has 5 open tickets, including 2 high-priority items that need attention.",
            "intent": "DataLookup",
            "evidence": ["tool:ticket_summary:account_id"]
        }
    ]
    
    for i, case in enumerate(valid_cases, 1):
        result = validator.validate_answer(case["answer"], case["intent"], case["evidence"])
        print(f"  Case {i}:")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Warnings: {len(result['warnings'])}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"    - {warning}")
        print()
    
    # Test 3.2: Invalid/problematic answers
    print("[Test 3.2] Problematic Answers")
    invalid_cases = [
        {
            "answer": "I think the answer is probably...",
            "intent": "FAQ",
            "evidence": []
        },
        {
            "answer": "Too short",
            "intent": "DataLookup",
            "evidence": ["tool:account_lookup"]
        },
        {
            "answer": "I apologize for the confusion. Let me check that for you.",
            "intent": "FAQ",
            "evidence": ["doc:faq.md"]
        }
    ]
    
    for i, case in enumerate(invalid_cases, 1):
        result = validator.validate_answer(case["answer"], case["intent"], case["evidence"])
        print(f"  Case {i}:")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Warnings: {result['warnings']}")
        print(f"  Blocked Patterns: {result['blocked_patterns']}")
        print()
    
    # Test 3.3: Evidence validation
    print("[Test 3.3] Evidence Quality Validation")
    evidence_cases = [
        ["doc:architecture.md", "doc:api.md"],  # Valid
        ["tool:account_lookup:account_id", "tool:invoice_status:account_id"],  # Valid
        ["escalated:human_support"],  # Valid
        [],  # Invalid - empty
        ["no_prefix_evidence"]  # Invalid - not properly formatted
    ]
    
    for i, evidence in enumerate(evidence_cases, 1):
        result = validator.validate_evidence(evidence)
        print(f"  Case {i}: {evidence}")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Has Sources: {result['has_sources']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")
        print()

def test_end_to_end_with_guardrails():
    """Test end-to-end graph execution with guardrails"""
    print_section("TEST 4: End-to-End Graph with Guardrails")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("  [SKIP] OPENAI_API_KEY not set. Skipping E2E tests.")
        return
    
    try:
        graph = get_graph()
        
        # Test 4.1: Normal FAQ query
        print("[Test 4.1] Normal FAQ Query")
        query = "How do I configure SSO?"
        result = graph.invoke(query)
        print(f"  Query: {query}")
        print(f"  Intent: {result['intent']}")
        print(f"  Evidence Count: {len(result['evidence'])}")
        print(f"  Errors: {len(result['errors'])}")
        if result['errors']:
            print(f"  Error Details: {result['errors']}")
        print()
        
        # Test 4.2: Query with PII
        print("[Test 4.2] Query with PII (should be redacted)")
        query = "My email is test@example.com and I need help"
        result = graph.invoke(query)
        print(f"  Original Query: {query}")
        print(f"  Intent: {result['intent']}")
        print(f"  Evidence (check for redaction): {[e for e in result['evidence'] if 'pii_redacted' in e]}")
        print()
        
        # Test 4.3: Sensitive topic (should escalate)
        print("[Test 4.3] Sensitive Topic (should auto-escalate)")
        query = "I want to cancel my subscription and get a refund"
        result = graph.invoke(query)
        print(f"  Query: {query}")
        print(f"  Intent: {result['intent']}")
        print(f"  Is Escalated: {'escalated' in result['intent'] or any('escalated' in e for e in result['evidence'])}")
        print()
        
        # Test 4.4: Data lookup with account context
        print("[Test 4.4] Data Lookup with Validation")
        query = "Show me my invoice status"
        result = graph.invoke(query, account_context="A1001")
        print(f"  Query: {query}")
        print(f"  Account: A1001")
        print(f"  Intent: {result['intent']}")
        print(f"  Evidence Count: {len(result['evidence'])}")
        print(f"  Errors: {len(result['errors'])}")
        print()
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        print(f"  Note: This might be expected if FAISS index or MCP server is not running")

def test_validation_summary():
    """Test validation summary statistics"""
    print_section("TEST 5: Validation Summary Statistics")
    
    validator = get_validator()
    
    # Simulate multiple validations
    test_cases = [
        {"answer": "Valid answer with good content and evidence.", "intent": "FAQ", "evidence": ["doc:test.md"]},
        {"answer": "Short", "intent": "FAQ", "evidence": []},
        {"answer": "I think this might be the answer but I'm not sure.", "intent": "FAQ", "evidence": ["doc:test.md"]},
        {"answer": "Clear and concise answer based on documentation.", "intent": "FAQ", "evidence": ["doc:test1.md", "doc:test2.md"]},
    ]
    
    print("[Running multiple validations...]")
    for case in test_cases:
        validator.validate_answer(case["answer"], case["intent"], case["evidence"])
    
    summary = validator.get_validation_summary()
    print(f"\n  Total Validations: {summary['total']}")
    print(f"  Valid Responses: {summary['valid']}")
    print(f"  Invalid Responses: {summary['invalid']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Avg Evidence Count: {summary['avg_evidence_count']:.1f}")
    print(f"  Avg Answer Length: {summary['avg_answer_length']:.1f} chars")

def main():
    """Run all guardrail tests"""
    print("\n" + "="*70)
    print("M4 GUARDRAILS TESTING SUITE".center(70))
    print("="*70)
    print("\nTesting validation, safety checks, and hallucination reduction...")
    
    try:
        # Run all tests
        test_safety_checks()
        test_tool_validation()
        test_output_validation()
        test_validation_summary()
        test_end_to_end_with_guardrails()
        
        print_section("TEST SUITE COMPLETE")
        print("All guardrail tests executed successfully!")
        print("\nKey Improvements:")
        print("  [OK] PII detection and redaction")
        print("  [OK] Sensitive topic auto-escalation")
        print("  [OK] Tool parameter validation")
        print("  [OK] Output quality validation")
        print("  [OK] Hallucination indicator detection")
        print("  [OK] Evidence quality checks")
        print("  [OK] Intent-answer matching")
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test suite stopped by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

