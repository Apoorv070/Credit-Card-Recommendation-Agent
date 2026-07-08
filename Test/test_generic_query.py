"""Test generic queries"""
from agent_graph import CreditCardAgent

agent = CreditCardAgent()

queries = [
    "My name is Apoorv btw i love travelling from flights",
    "Which card is best for travel?",
    "Tell me about credit card rewards",
    "I want a card for international travel"
]

for query in queries:
    print("\n" + "="*70)
    print(f"Query: {query}")
    print("="*70)
    
    result = agent.run(query)
    
    if result.get('final_recommendation'):
        print("\nResponse:")
        print(result['final_recommendation'])
    else:
        print(f"\nError: {result.get('error')}")
    
    print("\n")
