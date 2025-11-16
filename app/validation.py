"""
Output Validation and Safety Guardrails for NovaCRM Assistant

Provides validation and safety checks for:
- Input sanitization
- Output quality verification
- Hallucination detection
- Safety and compliance checks
"""

from typing import Dict, Any, List
import re

class OutputValidator:
    """
    Validates LLM outputs for quality and safety
    """
    
    def __init__(self):
        self.banned_content_patterns = [
            r"I apologize for the confusion",
            r"Let me check that for you",
            r"I'm just an AI",
            r"I don't have access to",
        ]
        # Statistics tracking
        self.stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "total_evidence": 0,
            "total_answer_length": 0
        }
    
    def validate_answer(self, answer: str, intent: str, evidence: List[str]) -> Dict[str, Any]:
        """
        Validate answer quality with intent context
        
        Args:
            answer: Generated answer
            intent: Query intent (FAQ, DataLookup, Escalation)
            evidence: Evidence list
            
        Returns:
            Validation result with is_valid flag and warnings list
        """
        warnings = []
        blocked_patterns = []
        
        # Check 1: Answer is not empty
        if not answer or len(answer.strip()) < 10:
            warnings.append("Answer is too short or empty")
        
        # Check 2: No banned phrases
        for pattern in self.banned_content_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                warnings.append(f"Contains banned phrase: {pattern}")
                blocked_patterns.append(pattern)
        
        # Check 3: Has evidence (except for Escalation)
        if intent != "Escalation" and not evidence:
            warnings.append("No evidence provided")
        
        # Check 4: Check for unsupported claims (basic heuristic)
        if "definitely" in answer.lower() or "certainly" in answer.lower():
            if not evidence or len(evidence) < 2:
                warnings.append("Strong claim without sufficient evidence")
        
        # Check 5: Length check (not too verbose)
        if len(answer) > 2500:
            warnings.append("Answer is excessively long")
        
        # Check 6: FAQ should have source citations
        if intent == "FAQ" and "Sources:" not in answer and len(evidence) > 0:
            warnings.append("FAQ answer missing explicit source citations")
        
        # Update statistics
        is_valid = len(warnings) == 0
        self.stats["total"] += 1
        if is_valid:
            self.stats["valid"] += 1
        else:
            self.stats["invalid"] += 1
        self.stats["total_evidence"] += len(evidence)
        self.stats["total_answer_length"] += len(answer)
        
        return {
            "is_valid": is_valid,
            "warnings": warnings,
            "blocked_patterns": blocked_patterns,
            "answer_length": len(answer),
            "evidence_count": len(evidence)
        }
    
    def validate_evidence(self, evidence: List[str]) -> Dict[str, Any]:
        """
        Validate evidence quality and completeness
        
        Args:
            evidence: List of evidence strings
            
        Returns:
            Validation result
        """
        warnings = []
        
        # Check evidence count
        if len(evidence) == 0:
            warnings.append("No evidence collected")
        
        # Check evidence types
        evidence_types = set()
        for e in evidence:
            if ":" in e:
                evidence_types.add(e.split(":")[0])
        
        # Check for diverse evidence sources
        if len(evidence_types) == 0:
            warnings.append("Evidence has no type tags")
        
        return {
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
            "has_sources": len(evidence) > 0,
            "evidence_count": len(evidence),
            "evidence_types": list(evidence_types)
        }
    
    def check_intent_answer_match(self, intent: str, answer: str, evidence: List[str]) -> bool:
        """
        Check if answer matches expected intent
        
        Args:
            intent: Query intent
            answer: Generated answer
            evidence: Evidence list
            
        Returns:
            True if answer matches intent expectations
        """
        if intent == "FAQ":
            # FAQ should have document evidence
            has_doc_evidence = any("doc:" in e for e in evidence)
            return has_doc_evidence
        
        elif intent == "DataLookup":
            # DataLookup should have tool evidence
            has_tool_evidence = any("tool:" in e for e in evidence)
            return has_tool_evidence
        
        elif intent == "Escalation":
            # Escalation should mention support contact info
            return "support" in answer.lower() or "contact" in answer.lower()
        
        return True  # Default: assume valid
    
    def sanitize_output(self, text: str) -> str:
        """
        Sanitize output text for safe display
        
        Args:
            text: Raw output text
            
        Returns:
            Sanitized text
        """
        # Remove potential code injection
        text = text.replace("<script>", "[script]")
        text = text.replace("</script>", "[/script]")
        
        # Remove excessive newlines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize user input query
        
        Args:
            query: Raw user query
            
        Returns:
            Sanitized query
        """
        # Remove excessive whitespace
        query = " ".join(query.split())
        
        # Remove potential injection attempts
        query = query.replace("```", "")
        query = query.replace("SYSTEM:", "")
        query = query.replace("Assistant:", "")
        
        # Truncate if too long
        if len(query) > 500:
            query = query[:500]
        
        return query.strip()
    
    def check_hallucination_indicators(self, answer: str, context: str = "") -> List[str]:
        """
        Check for potential hallucination indicators
        
        Args:
            answer: Generated answer
            context: Source context (optional)
            
        Returns:
            List of hallucination warnings
        """
        warnings = []
        
        # Check for specific numbers without context
        if re.search(r'\$\d{1,3}(,\d{3})*(\.\d{2})?', answer):
            if context and not re.search(r'\$\d', context):
                warnings.append("Answer contains specific prices not found in context")
        
        # Check for specific dates without context
        if re.search(r'\d{4}-\d{2}-\d{2}', answer):
            if context and len(re.findall(r'\d{4}-\d{2}-\d{2}', context)) == 0:
                warnings.append("Answer contains specific dates not found in context")
        
        # Check for absolute statements
        absolute_terms = ["always", "never", "impossible", "guaranteed", "100%"]
        for term in absolute_terms:
            if term in answer.lower():
                warnings.append(f"Contains absolute statement: '{term}'")
        
        return warnings
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all validations performed
        
        Returns:
            Dictionary with validation statistics
        """
        total = self.stats["total"]
        if total == 0:
            return {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "success_rate": 0.0,
                "avg_evidence_count": 0.0,
                "avg_answer_length": 0.0
            }
        
        return {
            "total": total,
            "valid": self.stats["valid"],
            "invalid": self.stats["invalid"],
            "success_rate": (self.stats["valid"] / total) * 100,
            "avg_evidence_count": self.stats["total_evidence"] / total,
            "avg_answer_length": self.stats["total_answer_length"] / total
        }

class SafetyGuardrails:
    """
    Safety checks and content filtering
    """
    
    def __init__(self):
        self.sensitive_patterns = [
            r"password",
            r"credit card",
            r"ssn",
            r"social security",
            r"api[_\s]?key",
            r"secret[_\s]?key",
        ]
        self.sensitive_topics = {
            "billing_dispute": ["refund", "charge", "billing error", "unauthorized charge"],
            "account_termination": ["cancel subscription", "close account", "delete account"],
            "data_breach": ["breach", "hacked", "compromised", "data leak"],
            "legal": ["lawsuit", "lawyer", "legal action", "sue"],
        }
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        }
    
    def check_input_safety(self, query: str) -> Dict[str, Any]:
        """
        Check if input query is safe
        
        Args:
            query: User query
            
        Returns:
            Safety check result
        """
        issues = []
        
        # Check for sensitive information requests
        for pattern in self.sensitive_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                issues.append(f"Query contains sensitive term: {pattern}")
        
        # Check for injection attempts
        if "{{" in query or "}}" in query:
            issues.append("Potential template injection detected")
        
        if "<script>" in query.lower():
            issues.append("Potential script injection detected")
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues
        }
    
    def check_output_safety(self, answer: str) -> Dict[str, Any]:
        """
        Check if output answer is safe to return
        
        Args:
            answer: Generated answer
            
        Returns:
            Safety check result
        """
        issues = []
        
        # Check for leaked sensitive patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                # Check if it's in a safe context (e.g., documentation reference)
                if "documentation" not in answer.lower() and "guide" not in answer.lower():
                    issues.append(f"Output may contain sensitive information: {pattern}")
        
        # Check for PII patterns
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', answer):  # SSN pattern
            issues.append("Output contains potential SSN pattern")
        
        if re.search(r'\b\d{16}\b', answer):  # Credit card pattern
            issues.append("Output contains potential credit card pattern")
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues
        }
    
    def check_sensitive_content(self, query: str) -> Dict[str, Any]:
        """
        Check if query contains sensitive topics that should be escalated
        
        Args:
            query: User query
            
        Returns:
            Sensitivity check result with matched topics and escalation flag
        """
        matched_topics = []
        query_lower = query.lower()
        
        # Check each sensitive topic
        for topic, keywords in self.sensitive_topics.items():
            for keyword in keywords:
                if keyword in query_lower:
                    matched_topics.append(topic)
                    break
        
        # Determine if should escalate
        should_escalate = len(matched_topics) > 0 and any(
            topic in ["legal", "data_breach"] for topic in matched_topics
        )
        
        return {
            "is_sensitive": len(matched_topics) > 0,
            "matched_topics": list(set(matched_topics)),
            "should_escalate": should_escalate
        }
    
    def check_pii_exposure(self, query: str) -> Dict[str, Any]:
        """
        Check if query contains PII and redact if necessary
        
        Args:
            query: User query
            
        Returns:
            PII check result with redacted text
        """
        pii_found = []
        redacted_text = query
        
        # Check and redact PII
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, query)
            if matches:
                pii_found.append(pii_type)
                # Redact PII
                redacted_text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", redacted_text)
        
        return {
            "has_pii": len(pii_found) > 0,
            "pii_types": pii_found,
            "redacted_text": redacted_text,
            "original_text": query
        }
    
    def validate_tool_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool parameters for safety and correctness
        
        Args:
            tool_name: Name of the tool
            params: Parameters to validate
            
        Returns:
            Validation result with is_valid flag and errors list
        """
        errors = []
        
        # Tool-specific validation
        if tool_name == "account_lookup":
            if "account_id" not in params and "company" not in params:
                errors.append("account_lookup requires either account_id or company parameter")
            if "account_id" in params:
                if not re.match(r'^A\d{3}$', params["account_id"]):
                    errors.append(f"Invalid account_id format: {params['account_id']}")
        
        elif tool_name == "invoice_status":
            if "account_id" not in params:
                errors.append("invoice_status requires account_id parameter")
            if "period" in params:
                if not re.match(r'^\d{4}-\d{2}$', params["period"]):
                    errors.append(f"Invalid period format: {params['period']}")
        
        elif tool_name == "ticket_summary":
            if "account_id" not in params:
                errors.append("ticket_summary requires account_id parameter")
            if "window_days" in params:
                try:
                    days = int(params["window_days"])
                    if days < 1 or days > 365:
                        errors.append("window_days must be between 1 and 365")
                except (ValueError, TypeError):
                    errors.append("window_days must be an integer")
        
        elif tool_name == "usage_report":
            if "account_id" not in params or "month" not in params:
                errors.append("usage_report requires account_id and month parameters")
            if "month" in params:
                if not re.match(r'^\d{4}-\d{2}$', params["month"]):
                    errors.append(f"Invalid month format: {params['month']}")
        
        elif tool_name == "kb_search":
            if "query" not in params:
                errors.append("kb_search requires query parameter")
            if "k" in params:
                try:
                    k = int(params["k"])
                    if k < 1 or k > 20:
                        errors.append("k must be between 1 and 20")
                except (ValueError, TypeError):
                    errors.append("k must be an integer")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

def get_validator() -> OutputValidator:
    """Factory function to get validator instance"""
    return OutputValidator()

def get_safety_guardrails() -> SafetyGuardrails:
    """Factory function to get safety guardrails instance"""
    return SafetyGuardrails()
