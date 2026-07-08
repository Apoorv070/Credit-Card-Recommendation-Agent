import re
import json
from typing import Dict, Any
import google.generativeai as genai
from agent_state import AgentState, INTENT_TYPES, SPEND_CATEGORIES, CONFIDENCE_LEVELS
from agent_tools import CreditCardTools
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Use models/gemini-1.0-pro (correct format for v1beta API)
model = genai.GenerativeModel('models/gemini-2.5-flash')

tools = CreditCardTools()


def intent_classification_node(state: AgentState) -> AgentState:
    """Node 1: Classify user intent"""
    
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    # Build conversation context for memory
    conversation_context = ""
    if len(messages) > 1:
        conversation_context = "\n\nPrevious conversation:\n"
        for msg in messages[:-1]:  # Exclude current query
            role = msg.get("role", "user")
            content = msg.get("content", "")[:200]  # Limit length
            conversation_context += f"{role.capitalize()}: {content}\n"
    
    prompt = f"""You are a credit card recommendation assistant. Classify the user's intent.
{conversation_context}
Current User Query: {user_query}

Intent Types:
- single_transaction: User wants recommendation for a single transaction
- monthly_optimization: User wants to optimize monthly spending across categories
- point_transfer: User wants point transfer strategy
- card_comparison: User wants to compare multiple cards
- general_query: General question about cards or rewards

Also determine:
- conversational_only: true if pure conversation (greetings, personal questions, chitchat) that doesn't need card data
- conversational_only: false if asking about card features, benefits, or recommendations (needs RAG)

Extract:
- spend_amount (if single transaction, in rupees)
- spend_category (if single transaction, one of: {', '.join(SPEND_CATEGORIES)})
- monthly_spending (if monthly optimization, dict of category: amount)

Respond in JSON format:
{{
    "intent": "intent_type",
    "conversational_only": true/false,
    "spend_amount": amount or null,
    "spend_category": "category" or null,
    "monthly_spending": {{"category1": amount1, "category2": amount2}} or null,
    "confidence": "high/medium/low"
}}

Example for monthly optimization:
User: "₹30,000 on dining, ₹40,000 on travel, ₹20,000 on groceries"
Response: {{"intent": "monthly_optimization", "monthly_spending": {{"dining": 30000, "flights": 40000, "groceries": 20000}}, "confidence": "high"}}
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        state["intent"] = result.get("intent", "general_query")
        state["conversational_only"] = result.get("conversational_only", False)
        state["spend_amount"] = result.get("spend_amount")
        state["spend_category"] = result.get("spend_category")
        state["monthly_spending"] = result.get("monthly_spending")
        state["confidence_level"] = result.get("confidence", "medium")
        
        if state["monthly_spending"]:
            print(f"\n🎯 Intent: {state['intent']}, Monthly Spending: {state['monthly_spending']}")
        else:
            print(f"\n🎯 Intent: {state['intent']}, Amount: {state['spend_amount']}, Category: {state['spend_category']}")
        
        # If pure conversation, skip RAG and go directly to final answer
        if state["conversational_only"]:
            print(f"   💬 Pure conversation - skipping RAG")
            state["next_step"] = "final_answer"
        else:
            state["next_step"] = "clarification"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Intent classified: {state['intent']}"
        })
        
    except Exception as e:
        print(f"\n❌ Intent classification error: {str(e)}")
        import traceback
        traceback.print_exc()
        state["error"] = f"Intent classification error: {str(e)}"
        state["intent"] = "general_query"
        state["spend_amount"] = None
        state["spend_category"] = None
        state["next_step"] = "clarification"
    
    return state


def clarification_node(state: AgentState) -> AgentState:
    """Node 2: Ask clarification questions if needed"""
    
    intent = state.get("intent")
    spend_amount = state.get("spend_amount")
    spend_category = state.get("spend_category")
    monthly_spending = state.get("monthly_spending")
    
    needs_clarification = False
    clarification_question = None
    
    if intent == "single_transaction":
        if not spend_amount:
            needs_clarification = True
            clarification_question = "What is the transaction amount you're planning to spend?"
        elif not spend_category:
            needs_clarification = True
            clarification_question = f"What category is this spend for? (e.g., {', '.join(SPEND_CATEGORIES[:5])})"
    
    elif intent == "monthly_optimization":
        if not monthly_spending:
            needs_clarification = True
            clarification_question = "Please provide your monthly spending amounts by category (e.g., Flights: ₹50,000, Hotels: ₹30,000)"
    
    state["needs_clarification"] = needs_clarification
    state["clarification_question"] = clarification_question
    
    if needs_clarification:
        state["messages"].append({
            "role": "assistant",
            "content": clarification_question
        })
        state["next_step"] = "wait_for_user"
    else:
        state["next_step"] = "retrieval"
    
    return state


def retrieval_node(state: AgentState) -> AgentState:
    """Node 3: Retrieve relevant card rules and context"""
    
    user_query = state["user_query"]
    intent = state.get("intent")
    spend_category = state.get("spend_category", "general")
    monthly_spending = state.get("monthly_spending")
    
    # For monthly optimization, retrieve for all categories
    if intent == "monthly_optimization" and monthly_spending:
        categories = list(monthly_spending.keys())
        query = f"{' '.join(categories)} rewards"
    else:
        query = f"{spend_category} rewards" if spend_category else user_query
    
    print(f"\n🔍 Query: {query}")
    print(f"   Card: All cards")
    
    try:
        result = tools.retrieve_card_rules(query, top_k=5)
        
        if result["success"]:
            state["retrieved_context"] = result["data"]
            state["messages"].append({
                "role": "assistant",
                "content": f"Retrieved context for {len(result['data']['cards_involved'])} cards"
            })
            state["next_step"] = "rule_validation"
        else:
            state["error"] = result["error"]
            state["next_step"] = "final_answer"
    
    except Exception as e:
        state["error"] = f"Retrieval error: {str(e)}"
        state["next_step"] = "final_answer"
    
    return state


def rule_validation_node(state: AgentState) -> AgentState:
    """Node 4: Validate retrieved rules"""
    
    retrieved_context = state.get("retrieved_context")
    
    if not retrieved_context:
        state["rule_validation_passed"] = False
        state["validation_message"] = "No context retrieved"
        state["next_step"] = "final_answer"
        return state
    
    reward_rules = retrieved_context.get("reward_rules", [])
    context_chunks = retrieved_context.get("context_chunks", [])
    
    if len(reward_rules) == 0 and len(context_chunks) == 0:
        state["rule_validation_passed"] = False
        state["validation_message"] = "No relevant rules found. Cannot make a reliable recommendation."
        state["next_step"] = "final_answer"
        print(f"   ❌ Validation failed: No rules or chunks")
    elif len(reward_rules) > 0:
        state["rule_validation_passed"] = True
        state["validation_message"] = f"Found {len(reward_rules)} structured rules"
        state["next_step"] = "calculation"
        print(f"   ✓ Validation passed: {len(reward_rules)} rules → next: calculation")
    else:
        state["rule_validation_passed"] = True
        state["validation_message"] = f"Found {len(context_chunks)} context chunks (no structured rules)"
        state["confidence_level"] = "medium"
        state["next_step"] = "calculation"
        print(f"   ✓ Validation passed: {len(context_chunks)} chunks → next: calculation")
    
    return state


def calculation_node(state: AgentState) -> AgentState:
    """Node 5: Calculate rewards for eligible cards"""
    
    print(f"\n💰 Calculation Node")
    retrieved_context = state.get("retrieved_context")
    intent = state.get("intent")
    spend_amount = state.get("spend_amount")
    spend_category = state.get("spend_category", "general")
    monthly_spending = state.get("monthly_spending")
    
    cards_involved = retrieved_context.get("cards_involved", [])
    if not cards_involved:
        cards_involved = tools.get_all_cards()[:3]
    
    calculations = []
    
    # Handle monthly optimization (multiple categories)
    if intent == "monthly_optimization" and monthly_spending:
        print(f"   Monthly Optimization Mode")
        print(f"   Categories: {list(monthly_spending.keys())}")
        
        for card_name in cards_involved:
            card_total = 0
            category_breakdown = {}
            
            for category, amount in monthly_spending.items():
                calc_result = tools.calculate_rewards(card_name, amount, category)
                if calc_result.get("success"):
                    card_total += calc_result.get("rupee_value", 0)
                    category_breakdown[category] = {
                        "amount": amount,
                        "points": calc_result.get("final_points", 0),
                        "rupee_value": calc_result.get("rupee_value", 0),
                        "reward_rate": calc_result.get("reward_rate", 0),
                        "is_capped": calc_result.get("is_capped", False),
                        "exclusions": calc_result.get("exclusions")
                    }
            
            calculations.append({
                "success": True,
                "card_name": card_name,
                "total_monthly_value": card_total,
                "category_breakdown": category_breakdown,
                "is_monthly_optimization": True
            })
            print(f"   {card_name}: Total ₹{card_total:,.2f}/month")
    
    # Handle single transaction
    else:
        print(f"   Amount: ₹{spend_amount}, Category: {spend_category}")
        
        # For general queries without amount, skip calculation
        if not spend_amount and intent == "general_query":
            print(f"   General query - skipping calculation")
            state["calculations"] = None
            state["next_step"] = "final_answer"
            return state
        
        if not spend_amount:
            state["error"] = "Cannot calculate without spend amount"
            state["next_step"] = "final_answer"
            return state
        
        for card_name in cards_involved:
            calc_result = tools.calculate_rewards(card_name, spend_amount, spend_category)
            calculations.append(calc_result)
            print(f"   Calculation for {card_name}: success={calc_result.get('success')}, error={calc_result.get('error')}")
    
    state["calculations"] = calculations
    state["messages"].append({
        "role": "assistant",
        "content": f"Calculated rewards for {len(calculations)} cards"
    })
    state["next_step"] = "comparison"
    
    return state


def comparison_node(state: AgentState) -> AgentState:
    """Node 6: Compare cards and rank them"""
    
    calculations = state.get("calculations", [])
    intent = state.get("intent")
    
    if not calculations:
        state["error"] = "No calculations to compare"
        state["next_step"] = "final_answer"
        return state
    
    # Handle monthly optimization - rank by total monthly value
    if intent == "monthly_optimization" and calculations[0].get("is_monthly_optimization"):
        rankings = sorted(
            [c for c in calculations if c.get("success")],
            key=lambda x: x.get("total_monthly_value", 0),
            reverse=True
        )
        
        if rankings:
            comparison_result = {
                "success": True,
                "best_card": rankings[0]["card_name"],
                "best_value": rankings[0]["total_monthly_value"],
                "rankings": [
                    {
                        "rank": i+1,
                        "card_name": r["card_name"],
                        "rupee_value": r["total_monthly_value"],
                        "category_breakdown": r.get("category_breakdown", {})
                    }
                    for i, r in enumerate(rankings)
                ],
                "is_monthly_optimization": True
            }
        else:
            comparison_result = {"success": False, "error": "No valid calculations"}
    
    # Handle single transaction
    else:
        comparison_result = tools.compare_cards(calculations)
    
    state["comparison_result"] = comparison_result
    
    if comparison_result.get("success"):
        state["messages"].append({
            "role": "assistant",
            "content": f"Best card: {comparison_result['best_card']} (₹{comparison_result['best_value']:.2f} value)"
        })
        state["next_step"] = "guardrails"
    else:
        state["error"] = comparison_result.get("error")
        state["next_step"] = "final_answer"
    
    return state


def guardrails_node(state: AgentState) -> AgentState:
    """Node 7: Apply guardrails and safety checks"""
    
    comparison_result = state.get("comparison_result", {})
    retrieved_context = state.get("retrieved_context", {})
    
    checks = {
        "has_retrieved_evidence": len(retrieved_context.get("reward_rules", [])) > 0 or len(retrieved_context.get("context_chunks", [])) > 0,
        "has_calculations": state.get("calculations") is not None,
        "has_comparison": comparison_result.get("success", False),
        "mentions_caps": False,
        "mentions_exclusions": False
    }
    
    warnings = []
    
    if not checks["has_retrieved_evidence"]:
        warnings.append("⚠️ Limited evidence - recommendation may not be accurate")
    
    calculations = state.get("calculations", [])
    for calc in calculations:
        if calc.get("is_capped"):
            checks["mentions_caps"] = True
        if calc.get("exclusions"):
            checks["mentions_exclusions"] = True
    
    if not checks["mentions_caps"]:
        warnings.append("⚠️ Monthly caps may apply - verify with card terms")
    
    if not checks["mentions_exclusions"]:
        warnings.append("⚠️ Exclusions may apply - verify merchant eligibility")
    
    state["guardrail_checks"] = checks
    state["guardrail_warnings"] = warnings
    
    state["next_step"] = "approval_gate"
    
    return state


def approval_gate_node(state: AgentState) -> AgentState:
    """Node 8: Determine if human approval needed"""
    
    intent = state.get("intent")
    confidence_level = state.get("confidence_level", "medium")
    spend_amount = state.get("spend_amount", 0)
    comparison_result = state.get("comparison_result", {})
    
    needs_approval = False
    approval_message = None
    
    # Trigger approval for point transfer strategies
    if intent == "point_transfer":
        needs_approval = True
        approval_message = "Point transfer strategies can be complex. Would you like me to proceed with detailed transfer routing analysis?"
    
    # Trigger approval for low confidence
    elif confidence_level == "low":
        needs_approval = True
        approval_message = "I have low confidence in this recommendation. Would you like me to proceed anyway?"
    
    # Trigger approval for high-value transactions (>₹2,00,000)
    elif spend_amount and spend_amount > 200000:
        needs_approval = True
        approval_message = f"This is a high-value transaction (₹{spend_amount:,.0f}). Would you like to review the recommendation before proceeding?"
    
    # Trigger approval if best card value is very close to second best (<5% difference)
    elif comparison_result.get('success') and len(comparison_result.get('rankings', [])) >= 2:
        rankings = comparison_result['rankings']
        best_value = rankings[0]['rupee_value']
        second_value = rankings[1]['rupee_value']
        
        if best_value > 0 and second_value > 0:
            difference_pct = (best_value - second_value) / best_value
            if difference_pct < 0.05:  # Less than 5% difference
                needs_approval = True
                approval_message = f"The top 2 cards have very similar rewards ({rankings[0]['card_name']}: ₹{best_value:,.0f} vs {rankings[1]['card_name']}: ₹{second_value:,.0f}). Would you like to review both options?"
    
    state["needs_approval"] = needs_approval
    state["approval_message"] = approval_message
    
    if needs_approval:
        state["next_step"] = "wait_for_approval"
    else:
        state["next_step"] = "final_answer"
    
    return state


def final_answer_node(state: AgentState) -> AgentState:
    """Node 9: Generate final recommendation"""
    
    error = state.get("error")
    if error:
        final_recommendation = f"❌ Error: {error}\n\nPlease rephrase your question or provide more details."
        state["final_recommendation"] = final_recommendation
        state["messages"].append({
            "role": "assistant",
            "content": final_recommendation
        })
        state["next_step"] = "end"
        return state
    
    comparison_result = state.get("comparison_result", {})
    calculations = state.get("calculations", [])
    retrieved_context = state.get("retrieved_context", {})
    guardrail_warnings = state.get("guardrail_warnings", [])
    intent = state.get("intent")
    spend_amount = state.get("spend_amount")
    spend_category = state.get("spend_category")
    monthly_spending = state.get("monthly_spending")
    user_query = state.get("user_query")
    
    # Handle conversational queries (with or without calculations)
    conversational_only = state.get("conversational_only", False)
    
    if (intent == "general_query" and calculations is None) or conversational_only:
        context_chunks = retrieved_context.get("context_chunks", []) if retrieved_context else []
        messages = state.get("messages", [])
        
        # Build conversation history for context
        conversation_history = ""
        if len(messages) > 1:
            conversation_history = "\n\nPrevious conversation:\n"
            for msg in messages[:-1]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:300]
                conversation_history += f"{role.capitalize()}: {content}\n"
        
        # Use LLM to generate contextual answer
        if context_chunks:
            context_text = "\n\n".join([f"Card: {chunk.get('card_name', 'Unknown')}\n{chunk.get('chunk_text', '')[:200]}" for chunk in context_chunks[:3]])
            context_section = f"\n\nCard Context:\n{context_text}"
        else:
            context_section = ""
        
        prompt = f"""You are a friendly credit card expert assistant. Answer this question based on the conversation history.
{conversation_history}
Current User Question: {user_query}
{context_section}

Instructions:
- If the user asks about their name or personal info from previous conversation, answer from conversation history
- If asking about card recommendations, suggest cards like Axis Atlas (travel), HDFC Infinia (premium), SBI Cashback (cashback)
- Keep responses warm, friendly, and personalized
- Use the user's name if you know it from previous messages

Answer:"""
        
        try:
            response = model.generate_content(prompt)
            final_recommendation = response.text.strip()
        except:
            final_recommendation = """I'd be happy to help with credit card recommendations!

For travel and flights, here are some great options:
- **Axis Bank Atlas**: Excellent for flights with 10x rewards on travel bookings
- **HDFC Infinia**: Premium card with 5x rewards on travel and dining
- **American Express Platinum Travel**: Great for international travel

Could you share more details about your spending patterns so I can give you a personalized recommendation?"""
        
        state["final_recommendation"] = final_recommendation
        state["messages"].append({
            "role": "assistant",
            "content": final_recommendation
        })
        state["next_step"] = "end"
        return state
    
    if not comparison_result.get("success"):
        final_recommendation = "Unable to generate recommendation. Please provide more details."
        state["final_recommendation"] = final_recommendation
        state["messages"].append({
            "role": "assistant",
            "content": final_recommendation
        })
        state["next_step"] = "end"
        return state
    
    best_card = comparison_result["best_card"]
    best_value = comparison_result["best_value"]
    rankings = comparison_result["rankings"]
    
    recommendation_parts = []
    
    # Handle monthly optimization
    if intent == "monthly_optimization" and comparison_result.get("is_monthly_optimization"):
        recommendation_parts.append(f"## 💳 Monthly Spend Optimization\n")
        recommendation_parts.append(f"### 🏆 Overall Best Card: **{best_card}**\n")
        recommendation_parts.append(f"**Total Monthly Value: ₹{best_value:,.2f}**\n")
        
        # Category-wise allocation recommendation
        recommendation_parts.append(f"\n### 📊 Category-Wise Card Allocation:\n")
        
        # Find best card for each category
        category_best = {}
        for category in monthly_spending.keys():
            best_for_category = None
            best_category_value = 0
            
            for calc in calculations:
                if calc.get("category_breakdown"):
                    cat_data = calc["category_breakdown"].get(category, {})
                    cat_value = cat_data.get("rupee_value", 0)
                    if cat_value > best_category_value:
                        best_category_value = cat_value
                        best_for_category = {
                            "card": calc["card_name"],
                            "value": cat_value,
                            "rate": cat_data.get("reward_rate", 0),
                            "exclusions": cat_data.get("exclusions")
                        }
            
            if best_for_category:
                category_best[category] = best_for_category
        
        # Generate recommendations per category
        for category, amount in monthly_spending.items():
            best_info = category_best.get(category)
            if best_info:
                recommendation_parts.append(
                    f"\n**{category.title()}** (₹{amount:,.0f}/month):\n"
                    f"- Use **{best_info['card']}** → ₹{best_info['value']:,.2f} value "
                    f"({best_info['rate']:.1f}x rewards)"
                )
                if best_info['exclusions']:
                    recommendation_parts.append(f"  - ⚠️ Exclusions: {best_info['exclusions']}")
        
        # Overall card rankings
        recommendation_parts.append(f"\n### 📈 Overall Card Rankings (Total Monthly Value):")
        for rank in rankings:
            recommendation_parts.append(
                f"\n{rank['rank']}. **{rank['card_name']}**: ₹{rank['rupee_value']:,.2f}/month"
            )
            
            # Show breakdown
            breakdown = rank.get('category_breakdown', {})
            if breakdown:
                for cat, data in breakdown.items():
                    recommendation_parts.append(
                        f"   - {cat.title()}: ₹{data['rupee_value']:,.2f} "
                        f"({data['reward_rate']:.1f}x)"
                    )
    
    # Handle single transaction
    else:
        best_calc = next((c for c in calculations if c.get("card_name") == best_card), None)
        
        recommendation_parts.append(f"## 💳 Recommendation for ₹{spend_amount:,.0f} {spend_category} spend\n")
        
        recommendation_parts.append(f"### 🏆 Best Card: **{best_card}**\n")
        recommendation_parts.append(f"**Estimated Value: ₹{best_value:,.2f}**\n")
    
        if best_calc:
            recommendation_parts.append(f"\n### 📊 Calculation Details:")
            recommendation_parts.append(f"- Reward Rate: {best_calc.get('reward_rate', 0):.2f} points per ₹")
            recommendation_parts.append(f"- Points Earned: {best_calc.get('final_points', 0):,.0f}")
            recommendation_parts.append(f"- Point Value (assumed): ₹{best_calc.get('point_value_assumption', 0.5):.2f} per point")
            
            if best_calc.get('is_capped'):
                recommendation_parts.append(f"- ⚠️ **Monthly cap applied**: {best_calc.get('monthly_cap', 0):,.0f} points")
            
            if best_calc.get('exclusions'):
                recommendation_parts.append(f"- ⚠️ **Exclusions**: {best_calc.get('exclusions')}")
            
            if best_calc.get('conditions'):
                recommendation_parts.append(f"- 📋 **Conditions**: {best_calc.get('conditions')}")
        
        recommendation_parts.append(f"\n### 📈 Card Comparison:")
        for rank in rankings:
            recommendation_parts.append(
                f"{rank['rank']}. **{rank['card_name']}**: ₹{rank['rupee_value']:,.2f} "
                f"({rank['points']:,.0f} points){' [CAPPED]' if rank['is_capped'] else ''}"
            )
    
    if retrieved_context.get("context_chunks"):
        recommendation_parts.append(f"\n### 📚 Evidence:")
        recommendation_parts.append(f"Retrieved {len(retrieved_context['context_chunks'])} relevant card rules")
    
    if guardrail_warnings:
        recommendation_parts.append(f"\n### ⚠️ Important Notes:")
        for warning in guardrail_warnings:
            recommendation_parts.append(f"- {warning}")
    
    recommendation_parts.append(f"\n### 🎯 Confidence: {state.get('confidence_level', 'medium').upper()}")
    
    recommendation_parts.append("\n---")
    recommendation_parts.append("*Always verify with official card terms before making decisions.*")
    
    final_recommendation = "\n".join(recommendation_parts)
    
    state["final_recommendation"] = final_recommendation
    state["messages"].append({
        "role": "assistant",
        "content": final_recommendation
    })
    state["next_step"] = "end"
    
    return state
