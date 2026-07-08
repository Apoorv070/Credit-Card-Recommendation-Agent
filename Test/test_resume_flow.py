"""Quick test for resume_after_approval functionality"""

from agent_graph import CreditCardAgent

agent = CreditCardAgent()

print("Testing HITL Resume Functionality")
print("="*60)

# Test high-value transaction
print("\n1. Running query that triggers approval...")
result = agent.run("I am spending ₹3,00,000 on flights")

if result.get("needs_approval"):
    print("✅ Approval triggered")
    print(f"   Message: {result.get('approval_message')}")
    
    # Test resume with approval
    print("\n2. Resuming with 'approved' decision...")
    final = agent.resume_after_approval(result, "approved")
    
    if final.get("final_recommendation"):
        print("✅ Resume successful!")
        print(f"   Recommendation: {final['final_recommendation'][:100]}...")
    else:
        print("❌ Resume failed")
else:
    print("❌ Approval not triggered")

print("\n" + "="*60)
print("Test complete!")
