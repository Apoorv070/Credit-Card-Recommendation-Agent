"""Debug monthly optimization"""
from agent_graph import CreditCardAgent

agent = CreditCardAgent()

query = "My monthly spends are ₹30,000 on dining, ₹40,000 on flights, ₹20,000 on groceries, and ₹15,000 on utilities. Suggest the best card-wise allocation."

print("Running query...")
result = agent.run(query)

print("\n" + "="*60)
print("DEBUG INFO")
print("="*60)
print(f"Intent: {result.get('intent')}")
print(f"Monthly Spending: {result.get('monthly_spending')}")
print(f"Needs Clarification: {result.get('needs_clarification')}")
print(f"Clarification Question: {result.get('clarification_question')}")
print(f"Error: {result.get('error')}")
print(f"Next Step: {result.get('next_step')}")
print(f"Retrieved Context: {result.get('retrieved_context') is not None}")
print(f"Rule Validation: {result.get('rule_validation_passed')}")
print(f"Has Calculations: {result.get('calculations') is not None}")
if result.get('calculations'):
    print(f"  Num Calculations: {len(result['calculations'])}")
print(f"Has Comparison: {result.get('comparison_result') is not None}")
if result.get('comparison_result'):
    print(f"  Best Card: {result['comparison_result'].get('best_card')}")
print(f"Has Final Rec: {result.get('final_recommendation') is not None}")

if result.get('final_recommendation'):
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    print(result['final_recommendation'][:500])
