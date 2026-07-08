"""
Visualize the LangGraph agent workflow
This creates a visual representation of the agent's decision flow
"""

def print_agent_flow():
    """Print ASCII visualization of the agent flow"""
    
    flow = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CREDIT CARD RECOMMENDATION AGENT FLOW                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  START: User Query from Streamlit UI                                        │
│  Example: "I am spending ₹50,000 on flights. Which card should I use?"     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 1: Intent Classification                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Tool: Google Gemini (LLM)                                          │   │
│  │  Input: user_query                                                  │   │
│  │  Output: intent, spend_amount, spend_category, confidence           │   │
│  │                                                                      │   │
│  │  Intent Types:                                                      │   │
│  │    • single_transaction                                             │   │
│  │    • monthly_optimization                                           │   │
│  │    • point_transfer                                                 │   │
│  │    • card_comparison                                                │   │
│  │    • general_query                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 2: Clarification                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Logic: Check if required info is missing                          │   │
│  │                                                                      │   │
│  │  If missing spend_amount:                                           │   │
│  │    → Ask: "What is the transaction amount?"                        │   │
│  │    → Set: needs_clarification = True                               │   │
│  │    → Return to user (wait_for_user)                                │   │
│  │                                                                      │   │
│  │  If missing spend_category:                                         │   │
│  │    → Ask: "What category? (flights, hotels, etc.)"                │   │
│  │    → Set: needs_clarification = True                               │   │
│  │    → Return to user (wait_for_user)                                │   │
│  │                                                                      │   │
│  │  If all info present:                                               │   │
│  │    → Set: needs_clarification = False                              │   │
│  │    → Continue to retrieval                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            needs_clarification?      needs_clarification?
                 = True                    = False
                    │                         │
                    ▼                         ▼
              WAIT_FOR_USER              CONTINUE
                  (END)                       │
                                              │
┌─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 3: Retrieval (TOOL CALL)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Tool: CreditCardTools.retrieve_card_rules()                        │   │
│  │                                                                      │   │
│  │  Step 1: FAISS Vector Search                                        │   │
│  │    Input: query = "{spend_category} rewards"                       │   │
│  │    Process:                                                          │   │
│  │      1. Generate query embedding (all-MiniLM-L6-v2)                │   │
│  │      2. Search FAISS index (170 chunks)                            │   │
│  │      3. Return top_k=5 most similar chunks                         │   │
│  │    Output: context_chunks = [chunk1, chunk2, ...]                  │   │
│  │                                                                      │   │
│  │  Step 2: SQLite Structured Query                                    │   │
│  │    Query: SELECT * FROM reward_rules                               │   │
│  │           WHERE spend_category = ?                                  │   │
│  │    Output: reward_rules = [rule1, rule2, ...]                      │   │
│  │                                                                      │   │
│  │  Combined Output:                                                    │   │
│  │    retrieved_context = {                                            │   │
│  │      "context_chunks": [...],                                       │   │
│  │      "reward_rules": [...],                                         │   │
│  │      "cards_involved": ["Axis Atlas", "HDFC DCB", ...]             │   │
│  │    }                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 4: Rule Validation                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Logic: Check quality of retrieved evidence                        │   │
│  │                                                                      │   │
│  │  If len(reward_rules) == 0 AND len(context_chunks) == 0:           │   │
│  │    → rule_validation_passed = False                                │   │
│  │    → validation_message = "No relevant rules found"               │   │
│  │    → confidence_level = "low"                                      │   │
│  │    → Skip to final_answer (with error)                             │   │
│  │                                                                      │   │
│  │  If len(reward_rules) > 0:                                          │   │
│  │    → rule_validation_passed = True                                 │   │
│  │    → confidence_level = "high"                                     │   │
│  │    → Continue to calculation                                        │   │
│  │                                                                      │   │
│  │  If len(context_chunks) > 0 but no structured rules:               │   │
│  │    → rule_validation_passed = True                                 │   │
│  │    → confidence_level = "medium"                                   │   │
│  │    → Continue to calculation                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 5: Calculation (TOOL CALL)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Tool: CreditCardTools.calculate_rewards()                          │   │
│  │                                                                      │   │
│  │  For each card in cards_involved:                                   │   │
│  │                                                                      │   │
│  │    1. Query SQLite for reward_rate:                                │   │
│  │       SELECT reward_rate, monthly_cap, exclusions                  │   │
│  │       FROM reward_rules                                             │   │
│  │       WHERE card_name = ? AND spend_category = ?                   │   │
│  │                                                                      │   │
│  │    2. Calculate base points:                                        │   │
│  │       base_points = spend_amount × reward_rate                     │   │
│  │                                                                      │   │
│  │    3. Apply monthly cap:                                            │   │
│  │       if monthly_cap AND base_points > monthly_cap:                │   │
│  │         final_points = monthly_cap                                  │   │
│  │         is_capped = True                                            │   │
│  │       else:                                                          │   │
│  │         final_points = base_points                                  │   │
│  │         is_capped = False                                           │   │
│  │                                                                      │   │
│  │    4. Convert to rupee value:                                       │   │
│  │       point_value = 0.5  (assumed)                                 │   │
│  │       rupee_value = final_points × point_value                     │   │
│  │                                                                      │   │
│  │  Output: calculations = [calc1, calc2, calc3, ...]                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 6: Comparison (TOOL CALL)                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Tool: CreditCardTools.compare_cards()                              │   │
│  │                                                                      │   │
│  │  1. Filter valid calculations (success = True)                      │   │
│  │                                                                      │   │
│  │  2. Sort by rupee_value (descending):                               │   │
│  │     Rank 1: Axis Atlas - ₹2,500                                    │   │
│  │     Rank 2: HDFC DCB - ₹1,875                                      │   │
│  │     Rank 3: SBI Cashback - ₹1,000                                  │   │
│  │                                                                      │   │
│  │  3. Generate comparison result:                                     │   │
│  │     comparison_result = {                                           │   │
│  │       "best_card": "Axis Atlas",                                    │   │
│  │       "best_value": 2500,                                           │   │
│  │       "rankings": [...]                                             │   │
│  │     }                                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 7: Guardrails Check                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Safety Checks:                                                      │   │
│  │                                                                      │   │
│  │  ✓ has_retrieved_evidence                                           │   │
│  │    → Check: len(context_chunks) > 0 OR len(reward_rules) > 0       │   │
│  │                                                                      │   │
│  │  ✓ has_calculations                                                 │   │
│  │    → Check: calculations is not None                               │   │
│  │                                                                      │   │
│  │  ✓ has_comparison                                                   │   │
│  │    → Check: comparison_result.success = True                       │   │
│  │                                                                      │   │
│  │  ✓ mentions_caps                                                    │   │
│  │    → Check: Any calculation has is_capped = True                   │   │
│  │    → If not: Add warning "Monthly caps may apply"                  │   │
│  │                                                                      │   │
│  │  ✓ mentions_exclusions                                              │   │
│  │    → Check: Any calculation has exclusions != null                 │   │
│  │    → If not: Add warning "Exclusions may apply"                    │   │
│  │                                                                      │   │
│  │  Output:                                                             │   │
│  │    guardrail_checks = {...}                                         │   │
│  │    guardrail_warnings = [...]                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 8: Approval Gate                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Logic: Determine if human approval needed                          │   │
│  │                                                                      │   │
│  │  If intent == "point_transfer":                                     │   │
│  │    → needs_approval = True                                          │   │
│  │    → approval_message = "Point transfer strategies are complex..." │   │
│  │    → Return to user (wait_for_approval)                            │   │
│  │                                                                      │   │
│  │  If confidence_level == "low":                                      │   │
│  │    → needs_approval = True                                          │   │
│  │    → approval_message = "Low confidence. Proceed anyway?"          │   │
│  │    → Return to user (wait_for_approval)                            │   │
│  │                                                                      │   │
│  │  Else:                                                               │   │
│  │    → needs_approval = False                                         │   │
│  │    → Continue to final_answer                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 9: Final Answer                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Generate formatted recommendation:                                 │   │
│  │                                                                      │   │
│  │  ## 💳 Recommendation for ₹50,000 flights spend                    │   │
│  │                                                                      │   │
│  │  ### 🏆 Best Card: **Axis Atlas**                                  │   │
│  │  **Estimated Value: ₹2,500**                                       │   │
│  │                                                                      │   │
│  │  ### 📊 Calculation Details:                                       │   │
│  │  - Reward Rate: 2.00 points per ₹                                  │   │
│  │  - Points Earned: 100,000                                           │   │
│  │  - Point Value: ₹0.50 per point                                    │   │
│  │  - ⚠️ Monthly cap applied: 100,000 points                         │   │
│  │                                                                      │   │
│  │  ### 📈 Card Comparison:                                           │   │
│  │  1. Axis Atlas: ₹2,500 (100,000 points)                           │   │
│  │  2. HDFC DCB: ₹1,875 (75,000 points)                              │   │
│  │  3. SBI Cashback: ₹1,000 (1,000 points)                           │   │
│  │                                                                      │   │
│  │  ### ⚠️ Important Notes:                                           │   │
│  │  - Monthly caps may apply                                           │   │
│  │  - Exclusions may apply                                             │   │
│  │                                                                      │   │
│  │  ### 🎯 Confidence: HIGH                                           │   │
│  │                                                                      │   │
│  │  *Always verify with official card terms*                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  END: Display in Streamlit UI                                               │
│  - Add to conversation history                                              │
│  - Update session state                                                     │
│  - Render formatted markdown                                                │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  KEY FEATURES:                                                                ║
║  • Grounded in retrieved evidence (no hallucination)                         ║
║  • Tool-based calculations (no LLM math)                                     ║
║  • Guardrails for safety                                                     ║
║  • Clarification for missing info                                            ║
║  • Approval gate for complex queries                                         ║
║  • Confidence levels                                                          ║
║  • Memory across conversation                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    print(flow)


def print_node_summary():
    """Print summary of each node"""
    
    summary = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           NODE SUMMARY                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 1: Intent Classification                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Understand what the user wants                                     │
│ Tool:     Google Gemini (LLM)                                                │
│ Input:    user_query                                                         │
│ Output:   intent, spend_amount, spend_category, confidence                   │
│ Duration: ~1-2 seconds                                                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 2: Clarification                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Ask for missing information                                        │
│ Tool:     Rule-based logic                                                   │
│ Input:    intent, spend_amount, spend_category                               │
│ Output:   needs_clarification, clarification_question                        │
│ Duration: <10ms                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 3: Retrieval                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Fetch relevant card rules and context                              │
│ Tool:     FAISS (vector search) + SQLite (structured query)                  │
│ Input:    query, card_name (optional)                                        │
│ Output:   context_chunks, reward_rules, cards_involved                       │
│ Duration: ~10-20ms                                                           │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 4: Rule Validation                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Check if retrieved evidence is sufficient                          │
│ Tool:     Rule-based logic                                                   │
│ Input:    retrieved_context                                                  │
│ Output:   rule_validation_passed, confidence_level                           │
│ Duration: <5ms                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 5: Calculation                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Calculate rewards for each card                                    │
│ Tool:     SQLite query + arithmetic                                          │
│ Input:    cards_involved, spend_amount, spend_category                       │
│ Output:   calculations (list of reward calculations)                         │
│ Duration: ~5-10ms per card                                                   │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 6: Comparison                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Rank cards by value                                                │
│ Tool:     Sorting algorithm                                                  │
│ Input:    calculations                                                       │
│ Output:   comparison_result (ranked cards)                                   │
│ Duration: <5ms                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 7: Guardrails                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Apply safety checks                                                │
│ Tool:     Rule-based validation                                              │
│ Input:    retrieved_context, calculations, comparison_result                 │
│ Output:   guardrail_checks, guardrail_warnings                               │
│ Duration: <5ms                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 8: Approval Gate                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Determine if human approval needed                                 │
│ Tool:     Rule-based logic                                                   │
│ Input:    intent, confidence_level                                           │
│ Output:   needs_approval, approval_message                                   │
│ Duration: <5ms                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Node 9: Final Answer                                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ Purpose:  Generate formatted recommendation                                  │
│ Tool:     String formatting                                                  │
│ Input:    All previous state                                                 │
│ Output:   final_recommendation (markdown formatted)                          │
│ Duration: <10ms                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

Total Response Time: ~2-3 seconds (mostly Gemini API call)
"""
    
    print(summary)


if __name__ == "__main__":
    print_agent_flow()
    print("\n\n")
    print_node_summary()
