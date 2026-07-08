# 🎯 Agent Evaluation Guide

Complete guide for evaluating the Credit Card Recommendation Agent.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Evaluation Framework](#evaluation-framework)
4. [Test Cases](#test-cases)
5. [Metrics](#metrics)
6. [Running Evaluation](#running-evaluation)
7. [Interpreting Results](#interpreting-results)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The evaluation framework tests the agent across **6 key dimensions**:

| Dimension | Description | Target Score |
|-----------|-------------|--------------|
| **Intent Classification** | Correctly identifying user intent | ≥95% |
| **Information Extraction** | Extracting amounts, categories, cards | ≥90% |
| **Retrieval Relevance** | Retrieving relevant cards/rules | ≥85% |
| **Calculation Accuracy** | Correct reward calculations | ≥90% |
| **Recommendation Quality** | Quality of final recommendations | ≥85% |
| **Clarification Handling** | Asking for clarification when needed | ≥80% |

**Overall Target**: ≥90% pass rate across all test cases

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install pandas
```

### Step 2: Run Evaluation

```bash
python run_evaluation.py
```

### Step 3: View Results

```bash
# View JSON report
cat evaluation/evaluation_report.json

# View CSV report
open evaluation/evaluation_report.csv
```

---

## 🏗️ Evaluation Framework

### Architecture

```
┌─────────────────┐
│  Test Cases     │
│  (JSON)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evaluator      │
│  Engine         │
└────────┬────────┘
         │
         ├──► Intent Classification
         ├──► Information Extraction
         ├──► Retrieval Relevance
         ├──► Calculation Accuracy
         ├──► Recommendation Quality
         └──► Clarification Handling
         │
         ▼
┌─────────────────┐
│  Reports        │
│  (JSON + CSV)   │
└─────────────────┘
```

### Components

1. **`test_cases.json`** - Test cases with expected outputs
2. **`evaluator.py`** - Evaluation engine
3. **`run_evaluation.py`** - Quick runner script
4. **Reports** - Generated evaluation results

---

## 🧪 Test Cases

### 10 Test Cases Covering:

#### 1. Single Transaction (TC001, TC002, TC005, TC009)
- Simple spend amount queries
- Tests: Intent, amount extraction, category, calculation

**Example**:
```
Query: "I am spending ₹50,000 on flights. Which card should I use?"
Expected: Axis Atlas or AmEx Platinum Travel
```

#### 2. Card Comparison (TC003)
- Comparing specific cards
- Tests: Intent, card identification, comparison logic

**Example**:
```
Query: "Compare Axis Atlas and HDFC Infinia for flight rewards"
Expected: Comparison of both cards
```

#### 3. General Query (TC004, TC008)
- Questions about card features
- Tests: Intent, retrieval, answer accuracy

**Example**:
```
Query: "What are the annual fees for HDFC Diners Club Black?"
Expected: Fee information
```

#### 4. Monthly Optimization (TC006)
- Multi-category spending
- Tests: Multi-category extraction, optimization logic

**Example**:
```
Query: "I spend ₹30,000 on dining and ₹20,000 on shopping monthly"
Expected: Optimized card recommendation
```

#### 5. Edge Cases (TC007, TC010)
- Ambiguous or unusual queries
- Tests: Clarification, edge case handling

**Example**:
```
Query: "Which card is best?"
Expected: Clarification question
```

#### 6. High Value Transactions (TC009)
- Large amounts testing cap logic
- Tests: Cap handling, calculation accuracy

**Example**:
```
Query: "I am spending ₹5,00,000 on flights"
Expected: Correct cap-aware calculation
```

---

## 📊 Metrics Explained

### 1. Intent Classification
**What**: Did the agent correctly identify user intent?

**Intents**:
- `single_transaction` - One-time spend query
- `card_comparison` - Compare multiple cards
- `monthly_optimization` - Optimize monthly spending
- `general_query` - General question
- `point_transfer` - Point transfer strategy

**Scoring**: Binary (0 or 1)

---

### 2. Information Extraction

#### Amount Extraction
**What**: Did the agent extract the correct spend amount?

**Example**:
- Query: "₹50,000 on flights"
- Expected: 50000
- Score: 1.0 if exact match

#### Category Extraction
**What**: Did the agent identify the correct spend category?

**Categories**: flights, hotels, dining, shopping, fuel, groceries, utilities, general

**Scoring**: Binary (0 or 1)

---

### 3. Retrieval Relevance
**What**: Did the agent retrieve relevant cards?

**Scoring**: 
```
score = (retrieved_cards ∩ expected_cards) / expected_cards
```

**Example**:
- Expected: [Axis Atlas, AmEx Platinum]
- Retrieved: [Axis Atlas, HDFC Infinia]
- Score: 1/2 = 0.5

---

### 4. Calculation Accuracy
**What**: Were reward calculations performed correctly?

**Checks**:
- Calculations exist
- Calculations have `success=True`
- Calculations have `rupee_value`

**Scoring**:
```
score = valid_calculations / total_calculations
```

---

### 5. Recommendation Quality
**What**: Is the final recommendation high quality?

**Quality Checks** (each worth 25%):
1. ✓ Has substantial recommendation (>50 chars)
2. ✓ Contains card name
3. ✓ Contains value/amount (₹)
4. ✓ No error messages

**Scoring**:
```
score = passed_checks / 4
```

**Pass Threshold**: ≥75% (3/4 checks)

---

### 6. Clarification Handling
**What**: Did the agent ask for clarification when needed?

**Scoring**: Binary (1.0 if clarification triggered)

---

## 🏃 Running Evaluation

### Method 1: Quick Run

```bash
python run_evaluation.py
```

**Output**:
```
🎯 CREDIT CARD AGENT EVALUATION
================================

Running Test Case: TC001 - single_transaction
Query: I am spending ₹50,000 on flights. Which card should I use?
================================

✓ Overall Score: 92.00%
✓ intent_classification: 100.00%
✓ amount_extraction: 100.00%
✓ category_extraction: 100.00%
✓ retrieval_relevance: 100.00%
✓ calculation_accuracy: 80.00%
✓ recommendation_quality: 75.00%

...

EVALUATION SUMMARY
==================

📊 Overall Performance:
   Total Tests: 10
   Passed: 8 (80.0%)
   Failed: 2
   Average Score: 85.0%

📈 Metric-wise Performance:
   intent_classification: 95.0%
   amount_extraction: 90.0%
   retrieval_relevance: 88.0%
   ...
```

### Method 2: Programmatic

```python
from evaluation.evaluator import AgentEvaluator

# Initialize
evaluator = AgentEvaluator()

# Run all tests
results = evaluator.run_all_tests()

# Get summary
summary = results['summary']
print(f"Pass Rate: {summary['pass_rate']:.1%}")

# Save reports
evaluator.save_report()
```

### Method 3: Single Test Case

```python
from evaluation.evaluator import AgentEvaluator

evaluator = AgentEvaluator()

# Run specific test
test_case = evaluator.test_cases[0]  # TC001
result = evaluator.run_test_case(test_case)

print(f"Score: {result['overall_score']:.1%}")
```

---

## 📈 Interpreting Results

### JSON Report Structure

```json
{
  "summary": {
    "total_tests": 10,
    "passed_tests": 8,
    "failed_tests": 2,
    "pass_rate": 0.8,
    "average_score": 0.85,
    "metric_scores": {
      "intent_classification": 0.95,
      "amount_extraction": 0.90,
      ...
    },
    "category_performance": {
      "single_transaction": {
        "pass_rate": 0.9,
        "avg_score": 0.87
      }
    }
  },
  "detailed_results": [
    {
      "test_case_id": "TC001",
      "passed": true,
      "overall_score": 0.92,
      "evaluations": [...],
      "agent_result": {...}
    }
  ]
}
```

### Key Metrics to Monitor

1. **Pass Rate** - % of tests passed (target: ≥90%)
2. **Average Score** - Average across all tests (target: ≥85%)
3. **Metric Scores** - Performance by dimension
4. **Category Performance** - Performance by test category

### Red Flags 🚩

- Pass rate < 70%
- Any metric < 80%
- Calculation accuracy < 85%
- Recommendation quality < 75%

---

## 🔍 Analyzing Failed Tests

### Step 1: Identify Failures

```bash
# View CSV
cat evaluation/evaluation_report.csv | grep "False"
```

### Step 2: Check Detailed Results

```python
import json

with open('evaluation/evaluation_report.json') as f:
    report = json.load(f)

for result in report['detailed_results']:
    if not result['passed']:
        print(f"\n❌ {result['test_case_id']}: {result['query']}")
        print(f"   Score: {result['overall_score']:.1%}")
        
        for eval in result['evaluations']:
            if not eval['passed']:
                print(f"   Failed: {eval['metric']}")
                print(f"   Expected: {eval.get('expected')}")
                print(f"   Actual: {eval.get('actual')}")
```

### Step 3: Debug Agent Output

```python
# Check full agent result
failed_result = report['detailed_results'][0]
agent_output = failed_result['agent_result']

print("Intent:", agent_output.get('intent'))
print("Amount:", agent_output.get('spend_amount'))
print("Category:", agent_output.get('spend_category'))
print("Recommendation:", agent_output.get('final_recommendation'))
```

---

## 🐛 Troubleshooting

### Issue: All Tests Failing

**Possible Causes**:
1. Gemini API not configured
2. Database/FAISS index missing
3. Agent initialization error

**Solution**:
```bash
# Check API key
echo $GOOGLE_API_KEY

# Check files exist
ls data/faiss_index.bin
ls database/credit_cards.db

# Test agent manually
python test_agent.py
```

---

### Issue: Low Intent Classification Score

**Possible Causes**:
1. Gemini model not working
2. Prompt needs improvement
3. Test expectations incorrect

**Solution**:
- Check `agent_nodes.py` intent classification prompt
- Verify Gemini API is working
- Review test case expected intents

---

### Issue: Low Calculation Accuracy

**Possible Causes**:
1. Missing reward rules in database
2. Card name mismatch
3. Calculation logic error

**Solution**:
```bash
# Check database
sqlite3 database/credit_cards.db "SELECT * FROM reward_rules;"

# Test calculation directly
python -c "
from agent_tools import CreditCardTools
tools = CreditCardTools()
result = tools.calculate_rewards('Axis Bank Atlas Credit Card', 50000, 'flights')
print(result)
"
```

---

### Issue: Low Retrieval Relevance

**Possible Causes**:
1. FAISS index outdated
2. Card names don't match
3. Embedding model issue

**Solution**:
- Rebuild FAISS index
- Check card name mapping in `local_rag_retriever.py`
- Verify embedding model loaded

---

## 📊 Performance Benchmarks

### Current Performance (Baseline)

| Metric | Score | Status |
|--------|-------|--------|
| Overall Pass Rate | TBD | 🟡 Pending |
| Intent Classification | TBD | 🟡 Pending |
| Amount Extraction | TBD | 🟡 Pending |
| Retrieval Relevance | TBD | 🟡 Pending |
| Calculation Accuracy | TBD | 🟡 Pending |
| Recommendation Quality | TBD | 🟡 Pending |

### Target Performance

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| Overall Pass Rate | ≥70% | ≥90% |
| Intent Classification | ≥85% | ≥95% |
| Amount Extraction | ≥80% | ≥90% |
| Retrieval Relevance | ≥75% | ≥85% |
| Calculation Accuracy | ≥80% | ≥90% |
| Recommendation Quality | ≥70% | ≥85% |

---

## 🎓 Best Practices

### 1. Regular Evaluation
- Run evaluation after every major change
- Track scores over time
- Set up CI/CD integration

### 2. Test Case Maintenance
- Add real user queries as test cases
- Update expected outputs when agent improves
- Remove outdated test cases

### 3. Continuous Improvement
- Focus on lowest-scoring metrics
- Analyze failed test patterns
- Iterate on agent prompts and logic

### 4. Documentation
- Document evaluation results
- Keep baseline scores
- Track improvements

---

## 📝 Adding New Test Cases

### Step 1: Create Test Case

Edit `evaluation/test_cases.json`:

```json
{
  "id": "TC011",
  "category": "your_category",
  "query": "Your test query here",
  "expected_intent": "single_transaction",
  "expected_category": "flights",
  "expected_amount": 50000,
  "expected_cards": ["Axis Bank Atlas Credit Card"],
  "evaluation_criteria": {
    "intent_classification": true,
    "amount_extraction": true,
    "category_extraction": true,
    "retrieval_relevance": true,
    "calculation_accuracy": true,
    "recommendation_quality": true
  }
}
```

### Step 2: Run Evaluation

```bash
python run_evaluation.py
```

### Step 3: Verify Results

Check if new test case appears in report.

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Agent Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evaluation
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: python run_evaluation.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-report
          path: evaluation/evaluation_report.*
```

---

## 📚 References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Agent Evaluation Best Practices](https://www.anthropic.com/index/evaluating-ai)
- [Test-Driven AI Development](https://martinfowler.com/articles/tdd-ai.html)

---

**Built with ❤️ for IIT Madras Agentic AI Capstone**

**Last Updated**: July 2026
