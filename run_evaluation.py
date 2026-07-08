#!/usr/bin/env python3
"""
Quick evaluation runner script
Run this to evaluate the agent performance
"""

import sys
import os
from evaluation.evaluator import AgentEvaluator

def main():
    print("\n" + "="*80)
    print("🎯 CREDIT CARD AGENT EVALUATION")
    print("="*80)
    
    print("\nInitializing evaluator...")
    evaluator = AgentEvaluator()
    
    print(f"Loaded {len(evaluator.test_cases)} test cases")
    
    # Run evaluation
    print("\nRunning evaluation...")
    evaluator.run_all_tests()
    
    # Print summary
    evaluator.print_summary()
    
    # Save reports
    print("\nSaving reports...")
    evaluator.save_report()
    
    print("\n✅ Evaluation complete!")
    print("\nReports generated:")
    print("  - evaluation/evaluation_report.json")
    print("  - evaluation/evaluation_report.csv")
    
    # Check if passed minimum criteria
    summary = evaluator.generate_summary()
    if summary['pass_rate'] >= 0.7:
        print(f"\n✅ PASSED: Agent meets minimum criteria ({summary['pass_rate']:.1%} pass rate)")
        return 0
    else:
        print(f"\n❌ FAILED: Agent below minimum criteria ({summary['pass_rate']:.1%} pass rate, need ≥70%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
