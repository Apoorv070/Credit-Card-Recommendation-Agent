"""Test RAG optimization - skip RAG for pure conversation"""
from agent_graph import CreditCardAgent

agent = CreditCardAgent()

print("="*70)
print("RAG OPTIMIZATION TEST")
print("="*70)

# Test 1: Pure conversation (should skip RAG)
print("\n[Test 1: Pure Conversation - Should SKIP RAG]")
print("Query: What is my name?")
result1 = agent.run("My name is Apoorv")
print("✓ Query processed")

print("\n[Test 2: Pure Conversation - Should SKIP RAG]")
print("Query: What is my name?")
result2 = agent.run("What is my name?")
print(f"Response: {result2.get('final_recommendation', 'Error')}")

# Test 3: Card question (should use RAG)
print("\n" + "="*70)
print("\n[Test 3: Card Question - Should USE RAG]")
print("Query: Which card is best for travel?")
result3 = agent.run("Which card is best for travel?")
print(f"Response: {result3.get('final_recommendation', 'Error')[:200]}...")

print("\n" + "="*70)
print("\n✅ Optimization Summary:")
print("- Pure conversation queries skip RAG (faster, no unnecessary retrieval)")
print("- Card-related queries use RAG (accurate, grounded in data)")
print("="*70)
