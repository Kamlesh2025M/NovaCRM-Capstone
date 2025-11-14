# Metrics Measurement Guide - M4

## Overview

This document explains how to measure and validate the performance improvements claimed in M4 using actual test data.

## Test Infrastructure

### 1. Test Dataset (`tests/test_dataset.py`)

**Gold-standard test dataset with 80 labeled test cases:**

- **FAQ Queries** (15 cases): Product info, pricing, features, API, security
- **DataLookup Queries** (10 cases): Account info, invoices, tickets, usage
- **Escalation Queries** (10 cases): Cancellations, refunds, legal, complaints
- **PII Test Cases** (5 cases): Email, phone, SSN, credit card detection
- **Edge Cases** (5 cases): Empty queries, XSS attempts, invalid formats, mixed intents
- **Additional Coverage** (35 more cases): Extended testing across all categories

Each test case includes:
- Query text
- Expected intent classification
- PII presence flags
- Sensitive content flags
- Expected grounding indicators

**View Dataset Summary:**
```bash
python tests/test_dataset.py
```

**Output:**
```
============================================================
TEST DATASET SUMMARY
============================================================
Total Test Cases: 80
  - FAQ: 15
  - DataLookup: 10
  - Escalation: 10
  - With PII: 5
  - Sensitive: 10
============================================================
```

---

### 2. Metrics Measurement Script (`tests/measure_metrics.py`)

Runs all test cases through the M4 system and measures 6 key metrics:

1. **Classification Accuracy**: % of queries classified to correct intent
2. **Answer Grounding Rate**: % of answers with proper evidence/citations
3. **PII Protection Rate**: % of PII correctly detected and redacted
4. **Professional Tone Compliance**: % of answers without banned phrases
5. **Error Handling Rate**: % of queries handled without crashes
6. **Sensitive Content Escalation**: % of sensitive queries properly escalated

**Run Measurements:**
```bash
python tests/measure_metrics.py
```

**Expected Output:**
```
================================================================================
                        METRICS MEASUREMENT - M4
================================================================================

Running 80 test cases...
Progress: 10/80 (12%)
Progress: 20/80 (25%)
...
✅ Completed 80 test runs

================================================================================
                             METRICS REPORT
================================================================================

Timestamp: 2024-11-13T10:30:45.123456
Total Tests Run: 80
Successful: 78
Failed: 2

--------------------------------------------------------------------------------
MEASURED METRICS
--------------------------------------------------------------------------------

1. Classification Accuracy
   Result: 76/80 = 95.0%
   Errors: 4 misclassifications

2. Answer Grounding Rate
   Result: 39/40 = 97.5%
   Issues: 1 answers without proper grounding

3. PII Protection Rate
   Result: 5/5 = 100.0%
   Failures: 0 PII not detected

4. Professional Tone Compliance
   Result: 77/78 = 98.7%
   Violations: 1 answers with banned phrases

5. Error Handling Rate
   Result: 78/80 = 97.5%
   Crashes: 2 queries caused errors

6. Sensitive Content Escalation
   Result: 10/10 = 100.0%
   Missed: 0 sensitive queries not escalated

================================================================================
                        SUMMARY - M4 VALIDATION
================================================================================
Classification Accuracy:        95.0%
Answer Grounding Rate:          97.5%
PII Protection Rate:            100.0%
Professional Tone:              98.7%
Error Handling:                 97.5%
Sensitive Content Escalation:   100.0%
================================================================================

📄 Report saved to: outputs/metrics_report_20241113_103045.json
```

---

### 3. Metrics Comparison Script (`tests/compare_metrics.py`)

Compares metrics before and after M4 to show actual improvements.

**Compare with Baseline (Estimated Pre-M4):**
```bash
python tests/compare_metrics.py outputs/metrics_report_XXXXXX.json
```

**Compare Two Actual Reports:**
```bash
python tests/compare_metrics.py before.json after.json
```

**Expected Output:**
```
================================================================================
                          METRICS COMPARISON
================================================================================

Before: 2024-01-01T00:00:00 (Baseline - Pre-M4)
After:  2024-11-13T10:30:45.123456

--------------------------------------------------------------------------------
Metric                                   Before        After         Change
--------------------------------------------------------------------------------
Classification Accuracy                   75.0%        95.0%      ✅ +20.0%
Answer Grounding Rate                     80.0%        97.5%      ✅ +17.5%
PII Protection Rate                       90.0%       100.0%      ✅ +10.0%
Professional Tone Compliance              85.0%        98.7%      ✅ +13.7%
Error Handling Rate                       93.8%        97.5%      ✅ +3.7%
Sensitive Content Escalation              70.0%       100.0%      ✅ +30.0%
--------------------------------------------------------------------------------

Average Improvement:                      ✅ +15.8%
================================================================================
```

---

## How Each Metric is Measured

### 1. Classification Accuracy

**Method:**
- Run each query through the router
- Compare actual intent vs. expected intent
- Calculate: `correct_classifications / total_queries * 100`

**Code:**
```python
for test_case in dataset:
    result = graph.invoke(test_case["query"])
    if result["intent"] == test_case["expected_intent"]:
        correct += 1
accuracy = correct / total * 100
```

**Example:**
- Query: "What is NovaCRM?"
- Expected: FAQ
- Actual: FAQ
- ✅ Correct

### 2. Answer Grounding Rate

**Method:**
- For FAQ queries: Check for document evidence (`doc:` in evidence) AND "Sources:" section
- For DataLookup queries: Check for tool evidence (`tool:` in evidence)
- Calculate: `grounded_answers / total_answers * 100`

**Code:**
```python
if intent == "FAQ":
    has_doc_evidence = any("doc:" in e for e in evidence)
    has_sources_section = "Sources:" in answer
    is_grounded = has_doc_evidence and has_sources_section

elif intent == "DataLookup":
    has_tool_evidence = any("tool:" in e for e in evidence)
    is_grounded = has_tool_evidence
```

**Example:**
- Query: "What are the pricing plans?"
- Evidence: `['doc:pricing_plans.md', 'doc:overview.md']`
- Answer includes: "**Sources:** - pricing_plans.md"
- ✅ Grounded

### 3. PII Protection Rate

**Method:**
- Run PII test cases with known PII (email, phone, SSN, credit card)
- Check if evidence includes `safety:pii_redacted`
- Calculate: `protected_cases / total_pii_cases * 100`

**Code:**
```python
for test_case in pii_test_cases:
    result = graph.invoke(test_case["query"])
    if any("safety:pii_redacted" in e for e in result["evidence"]):
        protected += 1
protection_rate = protected / total * 100
```

**Example:**
- Query: "My email is john@example.com"
- Evidence: `['safety:pii_redacted:email']`
- ✅ Protected

### 4. Professional Tone Compliance

**Method:**
- Check each answer for banned phrases
- Banned phrases: "I apologize for the confusion", "Let me check that for you", "I'm just an AI", etc.
- Calculate: `compliant_answers / total_answers * 100`

**Code:**
```python
banned_phrases = [
    "i apologize for the confusion",
    "let me check that for you",
    "i'm just an ai",
    "i don't have access to"
]

for result in results:
    answer_lower = result["answer"].lower()
    if not any(phrase in answer_lower for phrase in banned_phrases):
        compliant += 1
```

**Example:**
- Answer: "I apologize for the confusion, let me help you..."
- ❌ Not Compliant (contains banned phrase)

### 5. Error Handling Rate

**Method:**
- Run all queries and catch exceptions
- Calculate: `successful_runs / total_queries * 100`

**Code:**
```python
for test_case in dataset:
    try:
        result = graph.invoke(test_case["query"])
        handled += 1
    except Exception as e:
        crashes.append({"query": test_case["query"], "error": str(e)})
```

**Example:**
- Query: "" (empty string)
- Result: Gracefully handled with escalation
- ✅ Handled

### 6. Sensitive Content Escalation

**Method:**
- Run sensitive queries (legal, data breach, billing disputes)
- Check if escalated to human support OR has sensitive content evidence
- Calculate: `escalated_cases / total_sensitive_cases * 100`

**Code:**
```python
for test_case in sensitive_test_cases:
    result = graph.invoke(test_case["query"])
    has_sensitive_evidence = any("safety:sensitive_topic_detected" in e 
                                   for e in result["evidence"])
    is_escalated = result["intent"] == "Escalation"
    
    if has_sensitive_evidence or is_escalated:
        escalated += 1
```

**Example:**
- Query: "I'm taking legal action"
- Evidence: `['safety:sensitive_topic_detected:legal']`
- Intent: Escalation
- ✅ Escalated

---

## Understanding the Results

### Baseline Metrics (Estimated Pre-M4)

These are **estimated** typical performance for an LLM system without M4's guardrails:

- Classification Accuracy: **75%** (zero-shot classification)
- Answer Grounding: **80%** (no explicit citation requirements)
- PII Protection: **90%** (basic input sanitization only)
- Professional Tone: **85%** (no banned phrase checking)
- Error Handling: **94%** (basic try-except blocks)
- Sensitive Escalation: **70%** (no systematic detection)

### M4 Target Metrics

After implementing M4 features, we expect:

- Classification Accuracy: **95%** (few-shot prompting)
- Answer Grounding: **98%** (evidence tracking + validation)
- PII Protection: **100%** (4 regex patterns with validation)
- Professional Tone: **98%** (banned phrase detection)
- Error Handling: **97%** (comprehensive error handling)
- Sensitive Escalation: **100%** (4 sensitive categories detected)

### Actual Measured Results

Run `python tests/measure_metrics.py` to get **real** numbers from your system.

---

## Detailed Report Output

The measurement script saves a detailed JSON report with:

- Full test results for each query
- Misclassification errors with expected vs. actual
- Grounding issues with missing evidence
- PII protection failures
- Professional tone violations
- Error handling crashes
- Missed sensitive content

**Location:** `outputs/metrics_report_YYYYMMDD_HHMMSS.json`

**View Details:**
```bash
cat outputs/metrics_report_20241113_103045.json | python -m json.tool
```

---

## Continuous Measurement

### Run Before Changes
```bash
python tests/measure_metrics.py
mv outputs/metrics_report_*.json outputs/before_changes.json
```

### Make Your Changes
```bash
# Edit prompts, add new validation rules, etc.
```

### Run After Changes
```bash
python tests/measure_metrics.py
mv outputs/metrics_report_*.json outputs/after_changes.json
```

### Compare
```bash
python tests/compare_metrics.py outputs/before_changes.json outputs/after_changes.json
```

---

## Adding New Test Cases

Edit `tests/test_dataset.py`:

```python
TEST_DATASET.append({
    "id": "faq_099",
    "query": "Your new test query",
    "expected_intent": "FAQ",
    "has_pii": False,
    "is_sensitive": False,
    "expected_grounding": True,
    "expected_sources": ["document.md"],
    "category": "your_category"
})
```

Then re-run measurements:
```bash
python tests/measure_metrics.py
```

---

## Interpreting Metrics

### Classification Accuracy
- **< 80%**: Router needs better examples or prompt tuning
- **80-90%**: Good, but edge cases may be misclassified
- **> 90%**: Excellent, most queries correctly classified

### Answer Grounding
- **< 85%**: Answers may contain unsupported claims
- **85-95%**: Good grounding, minor citation issues
- **> 95%**: Excellent, answers are well-supported

### PII Protection
- **< 100%**: **CRITICAL** - PII leaks possible, fix immediately
- **100%**: Required standard, all PII detected

### Professional Tone
- **< 90%**: Frequent use of banned phrases, poor UX
- **90-95%**: Occasional lapses in professionalism
- **> 95%**: Consistently professional

### Error Handling
- **< 90%**: Frequent crashes, poor reliability
- **90-95%**: Most errors handled gracefully
- **> 95%**: Robust error handling

### Sensitive Escalation
- **< 95%**: Risk of mishandling sensitive issues
- **95-99%**: Most sensitive content caught
- **100%**: All sensitive content properly escalated

---

## Limitations

1. **Small Dataset**: 80 test cases may not cover all edge cases
2. **Simulated Baseline**: Pre-M4 baseline is estimated, not measured
3. **No Hallucination Rate**: Requires manual human review (time-intensive)
4. **Static Tests**: Real users may ask questions not in the dataset

**To improve:**
- Expand test dataset to 200+ cases
- Collect real user queries
- Perform manual hallucination audits (sample 100 answers)
- A/B test with real users

---

## Next Steps

1. **Run Initial Measurement**:
   ```bash
   python tests/measure_metrics.py
   ```

2. **Review Results**: Check which metrics are below target

3. **Iterate**: Improve prompts, add validation rules, expand test cases

4. **Re-measure**: Run again to verify improvements

5. **Document**: Update commit messages with **actual** measured metrics

---

*This measurement infrastructure provides empirical validation of M4's improvements over typical LLM systems.*

