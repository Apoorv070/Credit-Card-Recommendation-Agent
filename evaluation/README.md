# Agent Evaluation Framework

Comprehensive evaluation system for the Credit Card Recommendation Agent.

## 📋 Overview

This evaluation framework tests the agent across multiple dimensions:

1. **Intent Classification** - Correctly identifying user intent
2. **Information Extraction** - Extracting amounts, categories, card names
3. **Retrieval Relevance** - Retrieving relevant cards and rules
4. **Calculation Accuracy** - Correct reward calculations
5. **Recommendation Quality** - Quality of final recommendations
6. **Clarification Handling** - Asking for clarification when needed

## 🗂️ Structure

```
evaluation/
├── test_cases.json          # Test cases with expected outputs
├── evaluator.py             # Evaluation engine
├── README.md                # This file
├── evaluation_report.json   # Generated report (JSON)
└── evaluation_report.csv    # Generated report (CSV)
```

## 🧪 Test Cases

### Categories

1. **Single Transaction** - Simple spend amount queries
2. **Card Comparison** - Comparing multiple cards
3. **General Query** - Questions about card features
4. **Monthly Optimization** - Multi-category spending
5. **Edge Cases** - Unusual or challenging queries
6. **Clarification** - Ambiguous queries requiring clarification

### Test Case Format

```json
{
  "id": "TC001",
  "category": "single_transaction",
  "query": "I am spending ₹50,000 on flights. Which card should I use?",
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

## 🚀 Running Evaluation

### Basic Usage

```bash
cd /Users/apoorv.apoorv/Documents/Study/AgenticAIIITMadras/CapstroneProject
python evaluation/evaluator.py
```

### Programmatic Usage

```python
from evaluation.evaluator import AgentEvaluator

# Initialize evaluator
evaluator = AgentEvaluator()

# Run all tests
results = evaluator.run_all_tests()

# Print summary
evaluator.print_summary()

# Save report
evaluator.save_report()
```

## 📊 Evaluation Metrics

### 1. Intent Classification
- **Pass Criteria**: Correct intent identified
- **Score**: Binary (0 or 1)

### 2. Amount Extraction
- **Pass Criteria**: Exact amount match
- **Score**: Binary (0 or 1)

### 3. Category Extraction
- **Pass Criteria**: Correct category identified
- **Score**: Binary (0 or 1)

### 4. Retrieval Relevance
- **Pass Criteria**: At least one expected card retrieved
- **Score**: Overlap ratio (0 to 1)

### 5. Calculation Accuracy
- **Pass Criteria**: >50% valid calculations
- **Score**: Valid calculations / Total calculations

### 6. Recommendation Quality
- **Pass Criteria**: ≥75% quality score
- **Score**: Average of 4 checks:
  - Has substantial recommendation (>50 chars)
  - Contains card name
  - Contains value/amount
  - No error messages

### Overall Score
- Average of all applicable metric scores
- **Pass Threshold**: ≥70%

## 📈 Report Format

### JSON Report

```json
{
  "summary": {
    "total_tests": 10,
    "passed_tests": 8,
    "failed_tests": 2,
    "pass_rate": 0.8,
    "average_score": 0.85,
    "metric_scores": {
      "intent_classification": 0.9,
      "amount_extraction": 0.85,
      "retrieval_relevance": 0.88
    },
    "category_performance": {
      "single_transaction": {
        "pass_rate": 0.9,
        "avg_score": 0.87
      }
    }
  },
  "detailed_results": [...]
}
```

### CSV Report

| test_id | category | passed | overall_score | intent_classification | amount_extraction | ... |
|---------|----------|--------|---------------|----------------------|-------------------|-----|
| TC001   | single_transaction | True | 0.92 | 1.0 | 1.0 | ... |

## 🎯 Success Criteria

### Minimum Acceptable Performance

- **Overall Pass Rate**: ≥70%
- **Intent Classification**: ≥85%
- **Amount Extraction**: ≥80%
- **Retrieval Relevance**: ≥75%
- **Calculation Accuracy**: ≥80%
- **Recommendation Quality**: ≥70%

### Target Performance

- **Overall Pass Rate**: ≥90%
- **Intent Classification**: ≥95%
- **Amount Extraction**: ≥90%
- **Retrieval Relevance**: ≥85%
- **Calculation Accuracy**: ≥90%
- **Recommendation Quality**: ≥85%

## 🔧 Adding New Test Cases

1. Open `test_cases.json`
2. Add new test case following the format
3. Specify evaluation criteria
4. Run evaluation

Example:

```json
{
  "id": "TC011",
  "category": "your_category",
  "query": "Your test query",
  "expected_intent": "expected_intent",
  "expected_category": "expected_category",
  "expected_amount": 10000,
  "expected_cards": ["Card Name"],
  "evaluation_criteria": {
    "intent_classification": true,
    "amount_extraction": true
  }
}
```

## 📊 Analyzing Results

### View Summary
```bash
python evaluation/evaluator.py
```

### Analyze CSV
```python
import pandas as pd

df = pd.read_csv('evaluation/evaluation_report.csv')
print(df.describe())
print(df.groupby('category')['overall_score'].mean())
```

### View Detailed Results
```python
import json

with open('evaluation/evaluation_report.json') as f:
    report = json.load(f)
    
for result in report['detailed_results']:
    if not result['passed']:
        print(f"Failed: {result['test_case_id']}")
        print(f"Query: {result['query']}")
        print(f"Score: {result['overall_score']}")
```

## 🐛 Debugging Failed Tests

1. Check `evaluation_report.json` for detailed results
2. Look at `agent_result` field for full agent output
3. Compare `expected` vs `actual` values in evaluations
4. Check error messages if present

## 🔄 Continuous Evaluation

### Pre-deployment Checklist
- [ ] Run full evaluation suite
- [ ] Pass rate ≥70%
- [ ] No critical failures
- [ ] Review failed test cases
- [ ] Update test cases if needed

### Regression Testing
- Run evaluation after any code changes
- Compare results with baseline
- Investigate any score drops

## 📝 Notes

- Evaluation requires working agent setup
- Ensure GOOGLE_API_KEY is set
- Some tests may fail if Gemini API is unavailable
- Test cases can be extended based on real user queries
- Consider adding performance benchmarks (latency, etc.)

## 🎓 Evaluation Best Practices

1. **Regular Testing**: Run evaluation after every major change
2. **Baseline Tracking**: Keep historical evaluation results
3. **Test Coverage**: Add tests for edge cases and failures
4. **Real-world Queries**: Include actual user queries in test cases
5. **Performance Monitoring**: Track evaluation scores over time
