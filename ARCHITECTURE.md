# Agent Architecture Documentation

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                             │
│  - Chat Interface                                            │
│  - User Card Selection                                       │
│  - Conversation Memory                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGGRAPH AGENT                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 1: Intent Classification (Gemini)            │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 2: Clarification (if needed)                 │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 3: Retrieval (TOOL CALL)                     │    │
│  │  ├─ FAISS Vector Search (context chunks)           │    │
│  │  └─ SQLite Query (reward rules)                    │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 4: Rule Validation                           │    │
│  │  - Check confidence score                          │    │
│  │  - Verify evidence exists                          │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 5: Calculation (TOOL CALL)                   │    │
│  │  - Calculate rewards for each card                 │    │
│  │  - Apply caps and exclusions                       │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 6: Comparison (TOOL CALL)                    │    │
│  │  - Rank cards by value                             │    │
│  │  - Generate comparison table                       │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 7: Guardrails Check                          │    │
│  │  - Verify grounded in evidence                     │    │
│  │  - Check caps/exclusions mentioned                 │    │
│  │  - Set confidence level                            │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 8: Approval Gate                             │    │
│  │  - Check if human approval needed                  │    │
│  │  - Complex strategies require confirmation         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Node 9: Final Answer                              │    │
│  │  - Generate formatted recommendation               │    │
│  │  - Include calculation breakdown                   │    │
│  │  - Add warnings and disclaimers                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  FAISS Index     │  │  SQLite DB       │                │
│  │  - 170 chunks    │  │  - reward_rules  │                │
│  │  - Embeddings    │  │  - user_profiles │                │
│  │  - Metadata      │  │  - card_data     │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │  Local Embedding Model                   │              │
│  │  - all-MiniLM-L6-v2                      │              │
│  │  - Offline mode (no API calls)           │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Agent State Flow

### State Structure

```python
AgentState {
    # Input
    messages: List[Dict]          # Conversation history
    user_query: str               # Current query
    
    # Intent & Extraction
    intent: str                   # single_transaction, monthly_optimization, etc.
    spend_amount: float           # Extracted amount
    spend_category: str           # flights, hotels, dining, etc.
    user_cards: List[str]         # Cards owned by user
    
    # Clarification
    needs_clarification: bool     # Whether to ask follow-up
    clarification_question: str   # Question to ask
    
    # Retrieval
    retrieved_context: Dict       # FAISS chunks + SQLite rules
    
    # Validation
    rule_validation_passed: bool  # Whether evidence is sufficient
    validation_message: str       # Validation result
    
    # Calculation
    calculations: List[Dict]      # Reward calculations per card
    
    # Comparison
    comparison_result: Dict       # Ranked cards
    
    # Guardrails
    guardrail_checks: Dict        # Safety checks
    guardrail_warnings: List[str] # Warnings to show user
    
    # Approval
    needs_approval: bool          # Whether human approval needed
    approval_message: str         # Approval request message
    
    # Output
    final_recommendation: str     # Final formatted answer
    confidence_level: str         # high, medium, low
    error: str                    # Error message if any
    next_step: str                # Next node to execute
}
```

### State Transitions

```
START
  ↓
[user_query] → Intent Classification
  ↓
[intent, spend_amount, spend_category] → Clarification
  ↓
[needs_clarification = False] → Retrieval
  ↓
[retrieved_context] → Rule Validation
  ↓
[rule_validation_passed = True] → Calculation
  ↓
[calculations] → Comparison
  ↓
[comparison_result] → Guardrails
  ↓
[guardrail_checks, guardrail_warnings] → Approval Gate
  ↓
[needs_approval = False] → Final Answer
  ↓
[final_recommendation] → END
```

## 🛠️ Tools Architecture

### Tool 1: Retrieval Tool

```python
retrieve_card_rules(query, card_name=None, top_k=5)
  ↓
  ├─ FAISS Vector Search
  │  └─ Returns: context_chunks (text snippets from PDFs)
  │
  └─ SQLite Structured Query
     └─ Returns: reward_rules (structured reward rates)
  
Output: {
    "context_chunks": [...],
    "reward_rules": [...],
    "cards_involved": [...]
}
```

### Tool 2: Calculation Tool

```python
calculate_rewards(card_name, spend_amount, spend_category)
  ↓
  ├─ Query SQLite for reward_rate
  ├─ Calculate: base_points = spend_amount × reward_rate
  ├─ Apply monthly_cap if exists
  ├─ Convert points to rupee value
  └─ Return calculation breakdown

Output: {
    "card_name": "...",
    "base_points": 1000,
    "final_points": 1000,
    "is_capped": False,
    "rupee_value": 500,
    "exclusions": "...",
    "conditions": "..."
}
```

### Tool 3: Comparison Tool

```python
compare_cards(calculations)
  ↓
  ├─ Filter valid calculations
  ├─ Sort by rupee_value (descending)
  └─ Generate rankings

Output: {
    "best_card": "Axis Atlas",
    "best_value": 2500,
    "rankings": [
        {"rank": 1, "card_name": "...", "rupee_value": ...},
        {"rank": 2, "card_name": "...", "rupee_value": ...}
    ]
}
```

## 🧠 LLM Integration

### Google Gemini Usage

**Only used for:**
1. **Intent Classification** - Understanding user query
2. **Entity Extraction** - Extracting amount, category, card names
3. **Reasoning** - Explaining recommendations (future)

**NOT used for:**
- Reward calculations (uses SQLite data)
- Card comparisons (uses tool calculations)
- Inventing card rules (uses RAG retrieval)

### Prompt Structure

```python
prompt = f"""
You are a credit card recommendation assistant.

User Query: {user_query}

Intent Types:
- single_transaction
- monthly_optimization
- point_transfer
- card_comparison
- general_query

Extract:
- spend_amount (in rupees)
- spend_category (flights, hotels, etc.)

Respond in JSON format.
"""
```

## 🔒 Guardrails System

### Checks Performed

1. **Evidence Check**
   - ✓ Retrieved context exists
   - ✓ Rules are from database, not invented

2. **Calculation Check**
   - ✓ Calculations performed using tools
   - ✓ Not estimated or guessed

3. **Cap & Exclusion Check**
   - ✓ Monthly caps mentioned if applicable
   - ✓ Exclusions shown to user

4. **Confidence Check**
   - ✓ High: Strong evidence + structured rules
   - ✓ Medium: Context chunks only
   - ✓ Low: Limited evidence

5. **Safety Check**
   - ✓ Disclaimer added
   - ✓ User advised to verify with official terms

### Guardrail Output

```python
guardrail_checks = {
    "has_retrieved_evidence": True,
    "has_calculations": True,
    "has_comparison": True,
    "mentions_caps": True,
    "mentions_exclusions": False
}

guardrail_warnings = [
    "⚠️ Exclusions may apply - verify merchant eligibility"
]
```

## 💾 Memory System

### Conversation Memory (Session-based)

```python
# Stored in Streamlit session_state
conversation_history = [
    {
        "query": "I am spending ₹50,000 on flights",
        "response": "Recommendation: Axis Atlas...",
        "intent": "single_transaction",
        "confidence": "high"
    },
    ...
]
```

### User Profile Memory

```python
# Stored in session_state
user_cards = ["Axis Atlas", "HDFC Diners Club Black"]

# Future: Store in SQLite user_profiles table
```

### Context Window

- Maintains full conversation in Streamlit session
- Cleared on "Clear History" button
- Not persisted across sessions (future enhancement)

## 📊 Data Flow Example

### Example Query: "I am spending ₹50,000 on flights"

```
1. Intent Classification
   Input: "I am spending ₹50,000 on flights"
   Output: {
       intent: "single_transaction",
       spend_amount: 50000,
       spend_category: "flights"
   }

2. Clarification
   Check: spend_amount ✓, spend_category ✓
   Output: needs_clarification = False

3. Retrieval
   Query: "flights rewards"
   FAISS: Returns 5 chunks about flight rewards
   SQLite: Returns reward_rules for flights category
   Output: {
       context_chunks: [chunk1, chunk2, ...],
       reward_rules: [rule1, rule2, ...],
       cards_involved: ["Axis Atlas", "HDFC DCB", "SBI Cashback"]
   }

4. Rule Validation
   Check: reward_rules.length > 0 ✓
   Output: rule_validation_passed = True

5. Calculation
   For each card:
   - Axis Atlas: 50000 × 2 = 100,000 points = ₹2,500
   - HDFC DCB: 50000 × 1.5 = 75,000 points = ₹1,875
   - SBI Cashback: 50000 × 0.02 = ₹1,000 cashback
   
6. Comparison
   Rankings:
   1. Axis Atlas: ₹2,500
   2. HDFC DCB: ₹1,875
   3. SBI Cashback: ₹1,000

7. Guardrails
   Checks: All passed ✓
   Warnings: ["Monthly caps may apply"]

8. Approval Gate
   needs_approval = False (simple query)

9. Final Answer
   Generate formatted recommendation with:
   - Best card: Axis Atlas
   - Calculation breakdown
   - Comparison table
   - Warnings
   - Confidence: HIGH
```

## 🔄 Edge Cases Handled

1. **Missing Information**
   - Clarification node asks for amount/category
   - Waits for user response

2. **No Rules Found**
   - Rule validation fails
   - Returns error message instead of guessing

3. **Multiple Cards Tied**
   - Shows all top cards
   - Explains tie-breaker criteria

4. **Complex Queries**
   - Approval gate triggers
   - Asks user confirmation before proceeding

5. **Low Confidence**
   - Explicitly states uncertainty
   - Provides caveats and warnings

## 🚀 Performance Considerations

- **FAISS Search**: ~10ms for 170 chunks
- **SQLite Query**: ~5ms for reward rules
- **Gemini API**: ~1-2s for intent classification
- **Total Response Time**: ~2-3s per query

## 🔮 Future Architecture Enhancements

1. **Persistent Memory**
   - Store conversation history in SQLite
   - User profile management

2. **Multi-Agent System**
   - Separate agents for different intents
   - Supervisor agent for routing

3. **Advanced RAG**
   - Re-ranking retrieved chunks
   - Query expansion
   - Hybrid search (BM25 + vector)

4. **Evaluation Pipeline**
   - Automated testing with ground truth
   - Hallucination detection
   - Retrieval quality metrics

5. **Monitoring**
   - LangSmith integration
   - Query analytics dashboard
   - Error tracking and alerting
