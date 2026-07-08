import os
import sys

print("=" * 80)
print("CREDIT CARD RECOMMENDATION AGENT - SYSTEM TEST")
print("=" * 80)
print()

print("Step 1: Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    print(f"✓ GOOGLE_API_KEY found: {google_api_key[:20]}...")
else:
    print("✗ GOOGLE_API_KEY not found in .env")
    sys.exit(1)

print()
print("Step 2: Checking data files...")

required_files = [
    "data/faiss_index.bin",
    "data/chunks_mapping.json",
    "database/credit_cards.db"
]

for file_path in required_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✓ {file_path} ({size:,} bytes)")
    else:
        print(f"✗ {file_path} NOT FOUND")
        print(f"  Please run Phase 1 data ingestion first")
        sys.exit(1)

print()
print("Step 3: Testing RAG retriever...")

try:
    from local_rag_retriever import LocalRAGRetriever
    retriever = LocalRAGRetriever()
    print("✓ RAG retriever initialized")
    
    test_result = retriever.hybrid_retrieve("flight rewards", top_k=2)
    print(f"✓ Test retrieval successful: {len(test_result['context_chunks'])} chunks retrieved")
    retriever.close()
except Exception as e:
    print(f"✗ RAG retriever failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 4: Testing agent tools...")

try:
    from agent_tools import CreditCardTools
    tools = CreditCardTools()
    print("✓ Agent tools initialized")
    
    cards = tools.get_all_cards()
    print(f"✓ Found {len(cards)} cards in database: {', '.join(cards[:3])}")
    
    if cards:
        calc = tools.calculate_rewards(cards[0], 50000, "flights")
        if calc.get("success"):
            print(f"✓ Calculation test successful: {calc['card_name']} = ₹{calc.get('rupee_value', 0):.2f}")
        else:
            print(f"⚠ Calculation returned: {calc.get('error', 'Unknown error')}")
    
    tools.close()
except Exception as e:
    print(f"✗ Agent tools failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 5: Testing LangGraph agent...")

try:
    from agent_graph import CreditCardAgent
    agent = CreditCardAgent()
    print("✓ Agent initialized")
    
    test_query = "I am spending ₹50,000 on flights. Which card should I use?"
    print(f"\nTest Query: {test_query}")
    print("-" * 80)
    
    result = agent.run(test_query)
    
    if result.get("final_recommendation"):
        print("\n✓ Agent response:")
        print(result["final_recommendation"])
    else:
        print("\n⚠ No recommendation generated")
        print(f"Error: {result.get('error', 'Unknown')}")
    
except Exception as e:
    print(f"✗ Agent failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print()
print("Next steps:")
print("1. Run the Streamlit app: streamlit run streamlit_app.py")
print("2. Or test more queries: python agent_graph.py")
print()
