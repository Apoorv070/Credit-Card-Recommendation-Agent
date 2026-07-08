import config  # Load LangSmith configuration first
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_nodes import (
    intent_classification_node,
    clarification_node,
    retrieval_node,
    rule_validation_node,
    calculation_node,
    comparison_node,
    guardrails_node,
    approval_gate_node,
    final_answer_node
)


def create_agent_graph():
    """Create the LangGraph workflow for credit card recommendation"""
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("intent_classification", intent_classification_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("rule_validation", rule_validation_node)
    workflow.add_node("calculation", calculation_node)
    workflow.add_node("comparison", comparison_node)
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("approval_gate", approval_gate_node)
    workflow.add_node("final_answer", final_answer_node)
    
    workflow.set_entry_point("intent_classification")
    
    workflow.add_conditional_edges(
        "intent_classification",
        lambda state: state.get("next_step", "clarification"),
        {
            "clarification": "clarification",
            "final_answer": "final_answer"  # Skip RAG for pure conversation
        }
    )
    
    workflow.add_conditional_edges(
        "clarification",
        lambda state: state.get("next_step", "retrieval"),
        {
            "wait_for_user": END,
            "retrieval": "retrieval"
        }
    )
    
    workflow.add_edge("retrieval", "rule_validation")
    
    workflow.add_conditional_edges(
        "rule_validation",
        lambda state: state.get("next_step", "calculation"),
        {
            "calculation": "calculation",
            "final_answer": "final_answer"
        }
    )
    
    workflow.add_conditional_edges(
        "calculation",
        lambda state: state.get("next_step", "comparison"),
        {
            "comparison": "comparison",
            "final_answer": "final_answer"
        }
    )
    
    workflow.add_conditional_edges(
        "comparison",
        lambda state: state.get("next_step", "guardrails"),
        {
            "guardrails": "guardrails",
            "final_answer": "final_answer"
        }
    )
    
    workflow.add_edge("guardrails", "approval_gate")
    
    workflow.add_conditional_edges(
        "approval_gate",
        lambda state: state.get("next_step", "final_answer"),
        {
            "wait_for_approval": END,
            "final_answer": "final_answer"
        }
    )
    
    workflow.add_edge("final_answer", END)
    
    app = workflow.compile()
    
    return app


class CreditCardAgent:
    """Main agent class for credit card recommendations"""
    
    def __init__(self):
        self.graph = create_agent_graph()
        self.conversation_history = []
    
    def run(self, user_query: str, context: dict = None) -> dict:
        """
        Run the agent on a user query
        
        Args:
            user_query: User's question or request
            context: Optional context (user_cards, previous state, etc.)
            
        Returns:
            Final state with recommendation (may need approval)
        """
        
        # Include conversation history for memory
        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": user_query})
        
        initial_state = {
            "messages": messages,
            "user_query": user_query,
            "intent": None,
            "conversational_only": None,
            "spend_amount": None,
            "spend_category": None,
            "monthly_spending": None,
            "user_cards": context.get("user_cards") if context else None,
            "needs_clarification": False,
            "clarification_question": None,
            "retrieved_context": None,
            "rule_validation_passed": False,
            "validation_message": None,
            "calculations": None,
            "comparison_result": None,
            "guardrail_checks": None,
            "guardrail_warnings": None,
            "needs_approval": False,
            "approval_message": None,
            "final_recommendation": None,
            "confidence_level": None,
            "error": None,
            "next_step": None
        }
        
        final_state = self.graph.invoke(initial_state)
        
        # Update conversation history with user query and assistant response
        if not final_state.get("needs_approval"):
            # Add user message
            self.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            # Add assistant response
            if final_state.get("final_recommendation"):
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_state.get("final_recommendation")
                })
        
        return final_state
    
    def resume_after_approval(self, paused_state: dict, approval_decision: str) -> dict:
        """
        Resume workflow after human approval decision
        
        Args:
            paused_state: State that was paused at approval gate
            approval_decision: "approved", "rejected", or "clarify"
            
        Returns:
            Final state with recommendation
        """
        from agent_nodes import final_answer_node
        
        if approval_decision == "approved":
            # User approved - generate final answer from paused state
            final_state = final_answer_node(paused_state)
            
        elif approval_decision == "rejected":
            # User rejected - return rejection message
            final_state = paused_state.copy()
            final_state["final_recommendation"] = "❌ Recommendation rejected. Please provide more details or rephrase your question."
            
        elif approval_decision == "clarify":
            # User wants clarification
            final_state = paused_state.copy()
            final_state["final_recommendation"] = "🔄 I'll need more information. Could you please clarify your requirements?"
        
        else:
            final_state = paused_state.copy()
            final_state["final_recommendation"] = "Invalid approval decision."
        
        # Now add to conversation history with approval decision
        self.conversation_history.append({
            "query": paused_state.get("user_query"),
            "response": final_state.get("final_recommendation", "No recommendation generated"),
            "intent": paused_state.get("intent"),
            "confidence": paused_state.get("confidence_level"),
            "approval_decision": approval_decision
        })
        
        return final_state
    
    def get_conversation_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


if __name__ == "__main__":
    print("=" * 60)
    print("CREDIT CARD RECOMMENDATION AGENT TEST")
    print("=" * 60)
    print()
    
    agent = CreditCardAgent()
    
    test_queries = [
        "I am spending ₹50,000 on flights. Which card should I use?",
        "Compare Axis Atlas and HDFC Diners Club Black for hotel bookings"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        result = agent.run(query)
        
        print(result.get("final_recommendation", "No recommendation"))
        print()
