"""
Evaluation framework for Credit Card Recommendation Agent
Evaluates agent performance across multiple dimensions
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_graph import CreditCardAgent


class AgentEvaluator:
    """Evaluates agent performance on test cases"""
    
    def __init__(self, test_cases_path: str = "evaluation/test_cases.json"):
        """Initialize evaluator with test cases"""
        self.test_cases_path = test_cases_path
        self.agent = CreditCardAgent()
        self.results = []
        
        # Load test cases
        with open(test_cases_path, 'r') as f:
            data = json.load(f)
            self.test_cases = data['test_cases']
    
    def evaluate_intent_classification(self, result: Dict, expected_intent: str) -> Dict[str, Any]:
        """Evaluate if intent was correctly classified"""
        actual_intent = result.get('intent', 'unknown')
        correct = actual_intent == expected_intent
        
        return {
            'metric': 'intent_classification',
            'passed': correct,
            'expected': expected_intent,
            'actual': actual_intent,
            'score': 1.0 if correct else 0.0
        }
    
    def evaluate_amount_extraction(self, result: Dict, expected_amount: float) -> Dict[str, Any]:
        """Evaluate if spend amount was correctly extracted"""
        actual_amount = result.get('spend_amount')
        correct = actual_amount == expected_amount
        
        return {
            'metric': 'amount_extraction',
            'passed': correct,
            'expected': expected_amount,
            'actual': actual_amount,
            'score': 1.0 if correct else 0.0
        }
    
    def evaluate_category_extraction(self, result: Dict, expected_category: str) -> Dict[str, Any]:
        """Evaluate if spend category was correctly extracted"""
        actual_category = result.get('spend_category')
        correct = actual_category == expected_category
        
        return {
            'metric': 'category_extraction',
            'passed': correct,
            'expected': expected_category,
            'actual': actual_category,
            'score': 1.0 if correct else 0.0
        }
    
    def evaluate_retrieval_relevance(self, result: Dict, expected_cards: List[str]) -> Dict[str, Any]:
        """Evaluate if relevant cards were retrieved"""
        retrieved_context = result.get('retrieved_context', {})
        cards_involved = retrieved_context.get('cards_involved', [])
        
        # Check if at least one expected card was retrieved
        overlap = set(cards_involved) & set(expected_cards)
        relevance_score = len(overlap) / len(expected_cards) if expected_cards else 0.0
        
        return {
            'metric': 'retrieval_relevance',
            'passed': relevance_score > 0,
            'expected': expected_cards,
            'actual': cards_involved,
            'score': relevance_score
        }
    
    def evaluate_calculation_accuracy(self, result: Dict) -> Dict[str, Any]:
        """Evaluate if reward calculations were performed correctly"""
        calculations = result.get('calculations', [])
        
        if not calculations:
            return {
                'metric': 'calculation_accuracy',
                'passed': False,
                'error': 'No calculations performed',
                'score': 0.0
            }
        
        # Check if calculations have required fields
        valid_calcs = [c for c in calculations if c.get('success') and 'rupee_value' in c]
        accuracy_score = len(valid_calcs) / len(calculations) if calculations else 0.0
        
        return {
            'metric': 'calculation_accuracy',
            'passed': accuracy_score > 0.5,
            'total_calculations': len(calculations),
            'valid_calculations': len(valid_calcs),
            'score': accuracy_score
        }
    
    def evaluate_recommendation_quality(self, result: Dict) -> Dict[str, Any]:
        """Evaluate overall recommendation quality"""
        final_rec = result.get('final_recommendation', '')
        
        # Quality checks
        has_recommendation = len(final_rec) > 50
        has_card_name = any(card in final_rec for card in ['Axis', 'HDFC', 'SBI', 'American Express'])
        has_value = '₹' in final_rec or 'rupee' in final_rec.lower()
        no_error = 'error' not in final_rec.lower() and 'sorry' not in final_rec.lower()
        
        quality_score = sum([has_recommendation, has_card_name, has_value, no_error]) / 4.0
        
        return {
            'metric': 'recommendation_quality',
            'passed': quality_score >= 0.75,
            'has_recommendation': has_recommendation,
            'has_card_name': has_card_name,
            'has_value': has_value,
            'no_error': no_error,
            'score': quality_score
        }
    
    def evaluate_clarification(self, result: Dict) -> Dict[str, Any]:
        """Evaluate if clarification was triggered when needed"""
        needs_clarification = result.get('needs_clarification', False)
        clarification_question = result.get('clarification_question')
        
        return {
            'metric': 'clarification_triggered',
            'passed': needs_clarification,
            'clarification_question': clarification_question,
            'score': 1.0 if needs_clarification else 0.0
        }
    
    def run_test_case(self, test_case: Dict) -> Dict[str, Any]:
        """Run a single test case and evaluate results"""
        print(f"\n{'='*80}")
        print(f"Running Test Case: {test_case['id']} - {test_case['category']}")
        print(f"Query: {test_case['query']}")
        print(f"{'='*80}")
        
        try:
            # Run agent
            result = self.agent.run(test_case['query'])
            
            # Evaluate based on criteria
            evaluations = []
            criteria = test_case.get('evaluation_criteria', {})
            
            if criteria.get('intent_classification') and 'expected_intent' in test_case:
                evaluations.append(self.evaluate_intent_classification(
                    result, test_case['expected_intent']
                ))
            
            if criteria.get('amount_extraction') and 'expected_amount' in test_case:
                evaluations.append(self.evaluate_amount_extraction(
                    result, test_case['expected_amount']
                ))
            
            if criteria.get('category_extraction') and 'expected_category' in test_case:
                evaluations.append(self.evaluate_category_extraction(
                    result, test_case['expected_category']
                ))
            
            if criteria.get('retrieval_relevance') and 'expected_cards' in test_case:
                evaluations.append(self.evaluate_retrieval_relevance(
                    result, test_case['expected_cards']
                ))
            
            if criteria.get('calculation_accuracy'):
                evaluations.append(self.evaluate_calculation_accuracy(result))
            
            if criteria.get('recommendation_quality'):
                evaluations.append(self.evaluate_recommendation_quality(result))
            
            if criteria.get('clarification_triggered'):
                evaluations.append(self.evaluate_clarification(result))
            
            # Calculate overall score
            overall_score = sum(e['score'] for e in evaluations) / len(evaluations) if evaluations else 0.0
            
            test_result = {
                'test_case_id': test_case['id'],
                'category': test_case['category'],
                'query': test_case['query'],
                'passed': overall_score >= 0.7,
                'overall_score': overall_score,
                'evaluations': evaluations,
                'agent_result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Print summary
            print(f"\n✓ Overall Score: {overall_score:.2%}")
            for eval_result in evaluations:
                status = "✓" if eval_result['passed'] else "✗"
                print(f"{status} {eval_result['metric']}: {eval_result['score']:.2%}")
            
            return test_result
            
        except Exception as e:
            print(f"✗ Test case failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'test_case_id': test_case['id'],
                'category': test_case['category'],
                'query': test_case['query'],
                'passed': False,
                'overall_score': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases and generate report"""
        print("\n" + "="*80)
        print("CREDIT CARD AGENT EVALUATION")
        print("="*80)
        
        self.results = []
        
        for test_case in self.test_cases:
            result = self.run_test_case(test_case)
            self.results.append(result)
        
        # Generate summary
        summary = self.generate_summary()
        
        return {
            'summary': summary,
            'detailed_results': self.results,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate evaluation summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('passed', False))
        
        # Calculate average scores by metric
        metric_scores = {}
        for result in self.results:
            for eval_result in result.get('evaluations', []):
                metric = eval_result['metric']
                if metric not in metric_scores:
                    metric_scores[metric] = []
                metric_scores[metric].append(eval_result['score'])
        
        avg_metric_scores = {
            metric: sum(scores) / len(scores) if scores else 0.0
            for metric, scores in metric_scores.items()
        }
        
        # Category-wise performance
        category_performance = {}
        for result in self.results:
            category = result['category']
            if category not in category_performance:
                category_performance[category] = {'total': 0, 'passed': 0, 'scores': []}
            
            category_performance[category]['total'] += 1
            if result.get('passed', False):
                category_performance[category]['passed'] += 1
            category_performance[category]['scores'].append(result.get('overall_score', 0.0))
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0.0,
            'average_score': sum(r.get('overall_score', 0.0) for r in self.results) / total_tests if total_tests > 0 else 0.0,
            'metric_scores': avg_metric_scores,
            'category_performance': {
                cat: {
                    'pass_rate': perf['passed'] / perf['total'],
                    'avg_score': sum(perf['scores']) / len(perf['scores'])
                }
                for cat, perf in category_performance.items()
            }
        }
        
        return summary
    
    def save_report(self, output_path: str = "evaluation/evaluation_report.json"):
        """Save evaluation report to file"""
        report = {
            'summary': self.generate_summary(),
            'detailed_results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to: {output_path}")
        
        # Also save as CSV for easy analysis
        csv_path = output_path.replace('.json', '.csv')
        self.save_csv_report(csv_path)
    
    def save_csv_report(self, output_path: str):
        """Save evaluation results as CSV"""
        rows = []
        for result in self.results:
            row = {
                'test_id': result['test_case_id'],
                'category': result['category'],
                'passed': result.get('passed', False),
                'overall_score': result.get('overall_score', 0.0)
            }
            
            # Add metric scores
            for eval_result in result.get('evaluations', []):
                row[eval_result['metric']] = eval_result['score']
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        print(f"✓ CSV report saved to: {output_path}")
    
    def print_summary(self):
        """Print evaluation summary to console"""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        
        print(f"\n📊 Overall Performance:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']} ({summary['pass_rate']:.1%})")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Average Score: {summary['average_score']:.1%}")
        
        print(f"\n📈 Metric-wise Performance:")
        for metric, score in summary['metric_scores'].items():
            print(f"   {metric}: {score:.1%}")
        
        print(f"\n📂 Category-wise Performance:")
        for category, perf in summary['category_performance'].items():
            print(f"   {category}:")
            print(f"      Pass Rate: {perf['pass_rate']:.1%}")
            print(f"      Avg Score: {perf['avg_score']:.1%}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    evaluator = AgentEvaluator()
    evaluator.run_all_tests()
    evaluator.print_summary()
    evaluator.save_report()
