"""Test LangSmith tracing integration"""
import config  # This will load and configure LangSmith
from agent_graph import CreditCardAgent
from dotenv import load_dotenv
# import os
# from langsmith import Client

# # Load .env
# load_dotenv()

# print("API Key:", os.getenv("LANGSMITH_API_KEY"))
# print("Project:", os.getenv("LANGSMITH_PROJECT"))

# client = Client()

# for p in client.list_projects():
#     print(p.name)

print("="*70)
print("LANGSMITH TRACING TEST")
print("="*70)

# Check if LangSmith is enabled
if config.LANGSMITH_TRACING:
    print(f"\n✅ LangSmith tracing is ENABLED")
    print(f"   Project: {config.LANGSMITH_PROJECT}")
    print(f"   Endpoint: {config.LANGSMITH_ENDPOINT}")
else:
    print("\n⚠️  LangSmith tracing is DISABLED")
    print("   Set LANGSMITH_TRACING=true in .env to enable")

print("\n" + "="*70)
print("Running test query...")
print("="*70)

# Create agent and run a simple query
agent = CreditCardAgent()
result = agent.run("Which card is best for travel?")

print("\n✅ Query completed!")
print(f"Response: {result.get('final_recommendation', 'Error')[:150]}...")

print("\n" + "="*70)
print("CHECK LANGSMITH DASHBOARD:")
print("https://smith.langchain.com/")
print(f"Project: {config.LANGSMITH_PROJECT}")
print("="*70)
