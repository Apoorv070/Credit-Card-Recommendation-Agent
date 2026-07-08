"""
Test Human-in-the-Loop (HITL) approval system
"""

from agent_graph import CreditCardAgent

def test_hitl_scenarios():
    """Test different HITL approval scenarios"""
    
    agent = CreditCardAgent()
    
    print("\n" + "="*80)
    print("TESTING HUMAN-IN-THE-LOOP APPROVAL SYSTEM")
    print("="*80)
    
    # Test 1: High-value transaction (should trigger approval)
    print("\n" + "-"*80)
    print("Test 1: High-Value Transaction (₹3,00,000)")
    print("-"*80)
    
    result1 = agent.run("I am spending ₹3,00,000 on flights. Which card should I use?")
    
    if result1.get("needs_approval"):
        print("✅ PASS: Approval triggered for high-value transaction")
        print(f"   Message: {result1.get('approval_message')}")
        print(f"   Spend Amount: ₹{result1.get('spend_amount'):,}")
        
        # Test resume after approval
        print("\n   Testing resume_after_approval()...")
        final_result = agent.resume_after_approval(result1, "approved")
        if final_result.get("final_recommendation"):
            print("   ✅ Resume successful - final recommendation generated")
        else:
            print("   ❌ Resume failed - no final recommendation")
    else:
        print("❌ FAIL: Approval NOT triggered for high-value transaction")
    
    # Test 2: Normal transaction (should NOT trigger approval)
    print("\n" + "-"*80)
    print("Test 2: Normal Transaction (₹50,000)")
    print("-"*80)
    
    result2 = agent.run("I am spending ₹50,000 on flights. Which card should I use?")
    
    if not result2.get("needs_approval"):
        print("✅ PASS: Approval NOT triggered for normal transaction")
        print(f"   Spend Amount: ₹{result2.get('spend_amount'):,}")
    else:
        print("❌ FAIL: Approval incorrectly triggered for normal transaction")
        print(f"   Message: {result2.get('approval_message')}")
    
    # Test 3: Ambiguous query (may trigger low confidence)
    print("\n" + "-"*80)
    print("Test 3: Ambiguous Query")
    print("-"*80)
    
    result3 = agent.run("Which card is best?")
    
    print(f"   Needs Approval: {result3.get('needs_approval')}")
    print(f"   Confidence: {result3.get('confidence_level')}")
    if result3.get("needs_approval"):
        print(f"   Message: {result3.get('approval_message')}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    tests_passed = 0
    total_tests = 2  # Only counting definitive tests
    
    if result1.get("needs_approval"):
        tests_passed += 1
    if not result2.get("needs_approval"):
        tests_passed += 1
    
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Pass Rate: {tests_passed/total_tests*100:.0f}%")
    
    if tests_passed == total_tests:
        print("\n✅ ALL TESTS PASSED - HITL system working correctly!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review HITL configuration")
    
    print("\n" + "="*80)
    print("To test in UI, run: streamlit run streamlit_app.py")
    print("="*80)

if __name__ == "__main__":
    test_hitl_scenarios()
