"""
Test Monthly Spend Optimization feature
"""

from agent_graph import CreditCardAgent

def test_monthly_optimization():
    """Test monthly optimization with multiple categories"""
    
    agent = CreditCardAgent()
    
    print("\n" + "="*80)
    print("TESTING MONTHLY SPEND OPTIMIZATION")
    print("="*80)
    
    # Test query
    query = "My monthly spends are ₹30,000 on dining, ₹40,000 on flights, ₹20,000 on groceries, and ₹15,000 on utilities. Suggest the best card-wise allocation."
    
    print(f"\nQuery: {query}")
    print("\n" + "-"*80)
    
    result = agent.run(query)
    
    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    
    print(f"\nIntent: {result.get('intent')}")
    print(f"Monthly Spending: {result.get('monthly_spending')}")
    print(f"Needs Approval: {result.get('needs_approval')}")
    
    if result.get('final_recommendation'):
        print("\n" + "-"*80)
        print("RECOMMENDATION:")
        print("-"*80)
        print(result['final_recommendation'])
    else:
        print("\n⚠️ No final recommendation (may need approval)")
    
    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)

if __name__ == "__main__":
    test_monthly_optimization()
