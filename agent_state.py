from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """State for the credit card recommendation agent"""
    
    messages: List[Dict[str, str]]
    
    user_query: str
    
    intent: Optional[str]
    conversational_only: Optional[bool]
    
    spend_amount: Optional[float]
    spend_category: Optional[str]
    monthly_spending: Optional[Dict[str, float]]
    user_cards: Optional[List[str]]
    
    needs_clarification: bool
    clarification_question: Optional[str]
    
    retrieved_context: Optional[Dict[str, Any]]
    
    rule_validation_passed: bool
    validation_message: Optional[str]
    
    calculations: Optional[List[Dict[str, Any]]]
    
    comparison_result: Optional[Dict[str, Any]]
    
    guardrail_checks: Optional[Dict[str, bool]]
    guardrail_warnings: Optional[List[str]]
    
    needs_approval: bool
    approval_message: Optional[str]
    
    final_recommendation: Optional[str]
    
    confidence_level: Optional[str]
    
    error: Optional[str]
    
    next_step: Optional[str]


INTENT_TYPES = {
    "single_transaction": "User wants recommendation for a single transaction",
    "monthly_optimization": "User wants to optimize monthly spending across categories",
    "point_transfer": "User wants point transfer strategy",
    "card_comparison": "User wants to compare multiple cards",
    "general_query": "General question about cards or rewards"
}

SPEND_CATEGORIES = [
    "flights",
    "hotels", 
    "dining",
    "shopping",
    "fuel",
    "groceries",
    "utilities",
    "general"
]

CONFIDENCE_LEVELS = {
    "high": "Strong evidence from retrieved rules, clear calculation",
    "medium": "Some assumptions made, partial rule match",
    "low": "Limited evidence, multiple assumptions required"
}
