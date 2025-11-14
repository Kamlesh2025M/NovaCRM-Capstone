"""
Metrics Measurement Script

Runs test dataset through the system and measures actual performance metrics:
1. Classification Accuracy
2. Answer Grounding Rate
3. PII Protection Rate
4. Hallucination Rate (requires manual review)
5. Professional Tone Compliance
6. Error Handling Rate
"""

import sys
import os
from pathlib import Path
import json
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.graph import get_graph
from app.validation import get_validator, get_safety_guardrails
from tests.test_dataset import TEST_DATASET, get_summary

class MetricsCollector:
    """Collects and calculates metrics from test runs"""
    
    def __init__(self):
        self.graph = get_graph()
        self.validator = get_validator()
        self.safety = get_safety_guardrails()
        self.results = []
        
    def run_all_tests(self, verbose: bool = True) -> List[Dict[str, Any]]:
        """Run all test cases and collect results"""
        print("\n" + "=" * 80)
        print(" " * 25 + "METRICS MEASUREMENT - M4")
        print("=" * 80)
        print(f"\nRunning {len(TEST_DATASET)} test cases...")
        
        for i, test_case in enumerate(TEST_DATASET, 1):
            if verbose and i % 10 == 0:
                print(f"Progress: {i}/{len(TEST_DATASET)} ({i*100//len(TEST_DATASET)}%)")
            
            try:
                result = self.graph.invoke(
                    test_case["query"],
                    account_context=test_case.get("account_context")
                )
                
                self.results.append({
                    "test_id": test_case["id"],
                    "query": test_case["query"],
                    "expected_intent": test_case["expected_intent"],
                    "actual_intent": result["intent"],
                    "answer": result["answer"],
                    "evidence": result["evidence"],
                    "errors": result["errors"],
                    "test_case": test_case,
                    "success": True
                })
                
            except Exception as e:
                self.results.append({
                    "test_id": test_case["id"],
                    "query": test_case["query"],
                    "expected_intent": test_case["expected_intent"],
                    "actual_intent": None,
                    "answer": None,
                    "evidence": [],
                    "errors": [str(e)],
                    "test_case": test_case,
                    "success": False
                })
        
        print(f"✅ Completed {len(self.results)} test runs\n")
        return self.results
    
    def measure_classification_accuracy(self) -> Dict[str, Any]:
        """Measure intent classification accuracy"""
        correct = 0
        total = 0
        errors = []
        
        for result in self.results:
            if not result["success"]:
                continue
            
            total += 1
            expected = result["expected_intent"]
            actual = result["actual_intent"]
            
            if expected == actual:
                correct += 1
            else:
                errors.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "expected": expected,
                    "actual": actual
                })
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "metric": "Classification Accuracy",
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "errors": errors
        }
    
    def measure_answer_grounding(self) -> Dict[str, Any]:
        """Measure answer grounding rate (evidence-based answers)"""
        grounded = 0
        total = 0
        issues = []
        
        for result in self.results:
            if not result["success"]:
                continue
            
            intent = result["actual_intent"]
            answer = result["answer"] or ""
            evidence = result["evidence"]
            
            # Only check FAQ and DataLookup
            if intent not in ["FAQ", "DataLookup"]:
                continue
            
            total += 1
            
            # Check grounding
            is_grounded = False
            
            if intent == "FAQ":
                # FAQ should have document evidence and "Sources:" section
                has_doc_evidence = any("doc:" in e for e in evidence)
                has_sources_section = "Sources:" in answer or "sources:" in answer.lower()
                is_grounded = has_doc_evidence and has_sources_section
            
            elif intent == "DataLookup":
                # DataLookup should have tool evidence
                has_tool_evidence = any("tool:" in e for e in evidence)
                is_grounded = has_tool_evidence
            
            if is_grounded:
                grounded += 1
            else:
                issues.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "intent": intent,
                    "has_evidence": len(evidence) > 0,
                    "evidence_count": len(evidence)
                })
        
        grounding_rate = (grounded / total * 100) if total > 0 else 0
        
        return {
            "metric": "Answer Grounding Rate",
            "grounded": grounded,
            "total": total,
            "grounding_rate": grounding_rate,
            "issues": issues
        }
    
    def measure_pii_protection(self) -> Dict[str, Any]:
        """Measure PII detection and redaction rate"""
        protected = 0
        total = 0
        failures = []
        
        for result in self.results:
            test_case = result["test_case"]
            
            # Only check cases with PII
            if not test_case.get("has_pii", False):
                continue
            
            total += 1
            evidence = result["evidence"]
            
            # Check if PII was detected
            has_pii_evidence = any("safety:pii_redacted" in e for e in evidence)
            
            if has_pii_evidence:
                protected += 1
            else:
                failures.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "expected_pii_types": test_case.get("pii_types", []),
                    "evidence": evidence
                })
        
        protection_rate = (protected / total * 100) if total > 0 else 0
        
        return {
            "metric": "PII Protection Rate",
            "protected": protected,
            "total": total,
            "protection_rate": protection_rate,
            "failures": failures
        }
    
    def measure_professional_tone(self) -> Dict[str, Any]:
        """Measure professional tone compliance (no banned phrases)"""
        compliant = 0
        total = 0
        violations = []
        
        banned_phrases = [
            "i apologize for the confusion",
            "let me check that for you",
            "i'm just an ai",
            "i don't have access to"
        ]
        
        for result in self.results:
            if not result["success"] or not result["answer"]:
                continue
            
            total += 1
            answer_lower = result["answer"].lower()
            
            # Check for banned phrases
            found_phrases = [p for p in banned_phrases if p in answer_lower]
            
            if len(found_phrases) == 0:
                compliant += 1
            else:
                violations.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "banned_phrases_found": found_phrases,
                    "answer_snippet": result["answer"][:200]
                })
        
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        return {
            "metric": "Professional Tone Compliance",
            "compliant": compliant,
            "total": total,
            "compliance_rate": compliance_rate,
            "violations": violations
        }
    
    def measure_error_handling(self) -> Dict[str, Any]:
        """Measure error handling rate (no crashes)"""
        handled = 0
        total = len(self.results)
        crashes = []
        
        for result in self.results:
            if result["success"]:
                handled += 1
            else:
                crashes.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "error": result["errors"]
                })
        
        handling_rate = (handled / total * 100) if total > 0 else 0
        
        return {
            "metric": "Error Handling Rate",
            "handled": handled,
            "total": total,
            "handling_rate": handling_rate,
            "crashes": crashes
        }
    
    def measure_sensitive_content_escalation(self) -> Dict[str, Any]:
        """Measure sensitive content detection and escalation"""
        escalated = 0
        total = 0
        missed = []
        
        for result in self.results:
            test_case = result["test_case"]
            
            # Only check sensitive cases
            if not test_case.get("is_sensitive", False):
                continue
            
            total += 1
            evidence = result["evidence"]
            intent = result["actual_intent"]
            
            # Check if escalated or detected
            has_sensitive_evidence = any("safety:sensitive_topic_detected" in e for e in evidence)
            is_escalated = intent == "Escalation"
            
            if has_sensitive_evidence or is_escalated:
                escalated += 1
            else:
                missed.append({
                    "test_id": result["test_id"],
                    "query": result["query"],
                    "sensitive_category": test_case.get("sensitive_category", "unknown"),
                    "actual_intent": intent,
                    "evidence": evidence
                })
        
        escalation_rate = (escalated / total * 100) if total > 0 else 0
        
        return {
            "metric": "Sensitive Content Escalation",
            "escalated": escalated,
            "total": total,
            "escalation_rate": escalation_rate,
            "missed": missed
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics report"""
        dataset_summary = get_summary()
        
        metrics = {
            "classification_accuracy": self.measure_classification_accuracy(),
            "answer_grounding": self.measure_answer_grounding(),
            "pii_protection": self.measure_pii_protection(),
            "professional_tone": self.measure_professional_tone(),
            "error_handling": self.measure_error_handling(),
            "sensitive_escalation": self.measure_sensitive_content_escalation()
        }
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "dataset_summary": dataset_summary,
            "total_tests_run": len(self.results),
            "successful_runs": sum(1 for r in self.results if r["success"]),
            "failed_runs": sum(1 for r in self.results if not r["success"]),
            "metrics": metrics
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted metrics report"""
        print("\n" + "=" * 80)
        print(" " * 28 + "METRICS REPORT")
        print("=" * 80)
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Total Tests Run: {report['total_tests_run']}")
        print(f"Successful: {report['successful_runs']}")
        print(f"Failed: {report['failed_runs']}")
        
        print("\n" + "-" * 80)
        print("MEASURED METRICS")
        print("-" * 80)
        
        metrics = report['metrics']
        
        # 1. Classification Accuracy
        ca = metrics['classification_accuracy']
        print(f"\n1. {ca['metric']}")
        print(f"   Result: {ca['correct']}/{ca['total']} = {ca['accuracy']:.2f}%")
        if ca['errors']:
            print(f"   Errors: {len(ca['errors'])} misclassifications")
        
        # 2. Answer Grounding
        ag = metrics['answer_grounding']
        print(f"\n2. {ag['metric']}")
        print(f"   Result: {ag['grounded']}/{ag['total']} = {ag['grounding_rate']:.2f}%")
        if ag['issues']:
            print(f"   Issues: {len(ag['issues'])} answers without proper grounding")
        
        # 3. PII Protection
        pii = metrics['pii_protection']
        print(f"\n3. {pii['metric']}")
        print(f"   Result: {pii['protected']}/{pii['total']} = {pii['protection_rate']:.2f}%")
        if pii['failures']:
            print(f"   Failures: {len(pii['failures'])} PII not detected")
        
        # 4. Professional Tone
        pt = metrics['professional_tone']
        print(f"\n4. {pt['metric']}")
        print(f"   Result: {pt['compliant']}/{pt['total']} = {pt['compliance_rate']:.2f}%")
        if pt['violations']:
            print(f"   Violations: {len(pt['violations'])} answers with banned phrases")
        
        # 5. Error Handling
        eh = metrics['error_handling']
        print(f"\n5. {eh['metric']}")
        print(f"   Result: {eh['handled']}/{eh['total']} = {eh['handling_rate']:.2f}%")
        if eh['crashes']:
            print(f"   Crashes: {len(eh['crashes'])} queries caused errors")
        
        # 6. Sensitive Content Escalation
        se = metrics['sensitive_escalation']
        print(f"\n6. {se['metric']}")
        print(f"   Result: {se['escalated']}/{se['total']} = {se['escalation_rate']:.2f}%")
        if se['missed']:
            print(f"   Missed: {len(se['missed'])} sensitive queries not escalated")
        
        print("\n" + "=" * 80)
        print(" " * 25 + "SUMMARY - M4 VALIDATION")
        print("=" * 80)
        print(f"Classification Accuracy:        {ca['accuracy']:.1f}%")
        print(f"Answer Grounding Rate:          {ag['grounding_rate']:.1f}%")
        print(f"PII Protection Rate:            {pii['protection_rate']:.1f}%")
        print(f"Professional Tone:              {pt['compliance_rate']:.1f}%")
        print(f"Error Handling:                 {eh['handling_rate']:.1f}%")
        print(f"Sensitive Content Escalation:   {se['escalation_rate']:.1f}%")
        print("=" * 80 + "\n")
    
    def save_report(self, report: Dict[str, Any], filename: str = "metrics_report.json"):
        """Save report to JSON file"""
        output_dir = Path(__file__).resolve().parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filepath}")

def main():
    """Run metrics measurement"""
    import os
    from dotenv import load_dotenv
    
    # Load environment
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    # Run measurements
    collector = MetricsCollector()
    collector.run_all_tests(verbose=True)
    
    # Generate and print report
    report = collector.generate_report()
    collector.print_report(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    collector.save_report(report, f"metrics_report_{timestamp}.json")
    
    print("\n💡 TIP: Review detailed errors in the JSON report")
    print("   Location: outputs/metrics_report_*.json\n")

if __name__ == "__main__":
    main()

