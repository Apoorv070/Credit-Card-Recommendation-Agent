# 🤝 Human-in-the-Loop (HITL) Guide

Complete guide for the Human-in-the-Loop approval system in the Credit Card Recommendation Agent.

---

## 📋 Overview

The HITL system allows human oversight and approval for critical or uncertain recommendations, ensuring:
- **Safety**: High-value transactions require human review
- **Accuracy**: Low-confidence recommendations are flagged
- **Transparency**: Users can review and approve/reject recommendations
- **Control**: Users maintain final decision authority

---

## 🎯 When Approval is Triggered

The agent automatically requests human approval in these scenarios:

### 1. **High-Value Transactions** (>₹2,00,000)
```
User: "I am spending ₹5,00,000 on flights"
Agent: 🤔 This is a high-value transaction (₹5,00,000). 
       Would you like to review the recommendation before proceeding?
```

### 2. **Low Confidence Recommendations**
```
User: "Which card is best?"
Agent: 🤔 I have low confidence in this recommendation. 
       Would you like me to proceed anyway?
```

### 3. **Point Transfer Strategies**
```
User: "How should I transfer my points?"
Agent: 🤔 Point transfer strategies can be complex. 
       Would you like me to proceed with detailed transfer routing analysis?
```

### 4. **Close Competition** (<5% difference between top cards)
```
User: "Best card for ₹50,000 on flights?"
Agent: 🤔 The top 2 cards have very similar rewards 
       (Axis Atlas: ₹5,000 vs HDFC Infinia: ₹4,900). 
       Would you like to review both options?
```

---

## 🖥️ User Interface

### Approval Request Screen

When approval is needed, users see:

```
┌─────────────────────────────────────────────┐
│  🤔 Human Approval Required                 │
├─────────────────────────────────────────────┤
│  ℹ️ [Approval Message]                      │
│                                             │
│  📊 Preview Recommendation ▼                │
│     Best Card: Axis Bank Atlas              │
│     Estimated Value: ₹5,000.00              │
│                                             │
│     All Cards Ranked:                       │
│     1. Axis Bank Atlas - ₹5,000.00          │
│     2. HDFC Infinia - ₹4,900.00             │
│     3. AmEx Platinum - ₹4,500.00            │
│                                             │
│     Confidence Level: MEDIUM                │
│                                             │
│  [✅ Approve] [❌ Reject] [🔄 Request Clarification] │
└─────────────────────────────────────────────┘
```

### Three Actions Available

1. **✅ Approve**
   - Accepts the recommendation
   - Shows final recommendation in chat
   - Continues conversation

2. **❌ Reject**
   - Rejects the recommendation
   - Asks user to rephrase or provide more details
   - Clears pending approval

3. **🔄 Request Clarification**
   - Asks agent for more information
   - User can provide additional context
   - Restarts recommendation process

---

## 🔧 Technical Implementation

### Architecture

```
User Query
    ↓
Agent Processing
    ↓
Approval Gate Node
    ↓
[Needs Approval?]
    ├─ Yes → Pause & Show UI
    │         ↓
    │    User Decision
    │         ↓
    │    [Approve/Reject/Clarify]
    │         ↓
    └─ No  → Final Answer
```

### Code Components

#### 1. Agent State (`agent_state.py`)
```python
class AgentState(TypedDict):
    needs_approval: bool
    approval_message: Optional[str]
    # ... other fields
```

#### 2. Approval Gate Node (`agent_nodes.py`)
```python
def approval_gate_node(state: AgentState) -> AgentState:
    # Check conditions
    if spend_amount > 200000:
        needs_approval = True
    # ... other checks
    
    state["needs_approval"] = needs_approval
    return state
```

#### 3. Streamlit UI (`streamlit_app.py`)
```python
# Session state
st.session_state.pending_approval = None
st.session_state.approval_result = None

# Display approval UI
if st.session_state.pending_approval:
    display_approval_request(st.session_state.pending_approval)
```

---

## 📊 Approval Triggers Configuration

### Current Thresholds

| Trigger | Threshold | Configurable |
|---------|-----------|--------------|
| High-value transaction | >₹2,00,000 | ✅ Yes |
| Low confidence | confidence="low" | ✅ Yes |
| Close competition | <5% difference | ✅ Yes |
| Point transfer | intent="point_transfer" | ✅ Yes |

### Customizing Thresholds

Edit `agent_nodes.py`:

```python
# Change high-value threshold
elif spend_amount and spend_amount > 500000:  # Changed from 200000
    needs_approval = True

# Change close competition threshold
if difference_pct < 0.10:  # Changed from 0.05 (10% instead of 5%)
    needs_approval = True
```

---

## 🎯 Use Cases

### Use Case 1: High-Value Flight Booking

**Scenario**: User booking ₹3,00,000 flight

**Flow**:
1. User: "I'm spending ₹3,00,000 on flights"
2. Agent calculates rewards
3. Approval triggered (high-value)
4. User reviews:
   - Axis Atlas: ₹15,000 rewards
   - HDFC Infinia: ₹14,700 rewards
5. User approves
6. Agent provides detailed recommendation

**Benefit**: User reviews before committing to high-value transaction

---

### Use Case 2: Ambiguous Query

**Scenario**: Vague user query

**Flow**:
1. User: "Which card?"
2. Agent has low confidence
3. Approval triggered
4. User sees clarification request
5. User clicks "Request Clarification"
6. User provides: "Which card for ₹50,000 on hotels?"
7. Agent processes with full context

**Benefit**: Ensures accurate recommendations through clarification

---

### Use Case 3: Close Competition

**Scenario**: Two cards with similar rewards

**Flow**:
1. User: "Best card for ₹50,000 dining?"
2. Agent finds:
   - Card A: ₹2,500 (5% rewards)
   - Card B: ₹2,450 (4.9% rewards)
3. Approval triggered (<5% difference)
4. User reviews both options
5. User considers other factors (annual fee, benefits)
6. User makes informed decision

**Benefit**: Highlights close decisions for user consideration

---

## 📈 Metrics & Monitoring

### Track These Metrics

1. **Approval Rate**: % of queries requiring approval
2. **Approval Decision Distribution**:
   - % Approved
   - % Rejected
   - % Clarification requested
3. **Time to Decision**: How long users take to decide
4. **Approval Trigger Distribution**: Which triggers fire most

### Example Tracking

```python
# In streamlit_app.py
if st.session_state.approval_result == "approved":
    # Log approval
    log_approval_event({
        'trigger': approval_data.get('trigger_reason'),
        'decision': 'approved',
        'timestamp': datetime.now()
    })
```

---

## 🔒 Security & Safety

### Benefits

1. **Prevents Errors**: Human review catches mistakes
2. **Builds Trust**: Users see reasoning before committing
3. **Compliance**: Audit trail of approvals
4. **Risk Management**: High-value transactions reviewed

### Best Practices

1. **Clear Messaging**: Explain why approval is needed
2. **Show Context**: Display all relevant information
3. **Easy Actions**: Simple approve/reject/clarify buttons
4. **Timeout Handling**: Clear pending approvals after inactivity
5. **Logging**: Track all approval decisions

---

## 🎓 Advanced Features (Future)

### 1. Approval Policies
```python
# Define custom approval policies
APPROVAL_POLICIES = {
    'conservative': {
        'high_value_threshold': 100000,
        'confidence_threshold': 'medium'
    },
    'balanced': {
        'high_value_threshold': 200000,
        'confidence_threshold': 'low'
    },
    'aggressive': {
        'high_value_threshold': 500000,
        'confidence_threshold': 'low'
    }
}
```

### 2. Multi-Level Approval
```python
# Different approval levels
if spend_amount > 1000000:
    needs_approval = 'manager'  # Requires manager approval
elif spend_amount > 200000:
    needs_approval = 'user'  # Requires user approval
```

### 3. Approval History
```python
# Track approval history
st.session_state.approval_history = [
    {
        'query': '...',
        'decision': 'approved',
        'timestamp': '...',
        'reason': 'high_value'
    }
]
```

### 4. Auto-Approval Rules
```python
# Skip approval for trusted scenarios
if user_has_approved_similar_before():
    needs_approval = False
```

---

## 🐛 Troubleshooting

### Issue: Approval UI Not Showing

**Check**:
1. `needs_approval` is set in agent result
2. `pending_approval` is stored in session state
3. Streamlit is re-rendering after agent run

**Solution**:
```python
# Debug in streamlit_app.py
st.write("Debug:", st.session_state.pending_approval)
```

---

### Issue: Buttons Not Working

**Check**:
1. Button keys are unique
2. `st.rerun()` is called after button click
3. Session state is being updated

**Solution**:
```python
# Add debug logging
if st.button("Approve", key="approve_btn"):
    st.write("Button clicked!")  # Debug
    st.session_state.approval_result = "approved"
    st.rerun()
```

---

### Issue: Approval Triggers Too Often

**Solution**: Adjust thresholds in `agent_nodes.py`:
```python
# Make less sensitive
elif spend_amount and spend_amount > 500000:  # Higher threshold
    needs_approval = True
```

---

## 📝 Testing HITL

### Manual Testing

```bash
# Start Streamlit
streamlit run streamlit_app.py

# Test scenarios:
1. "I'm spending ₹3,00,000 on flights" → Should trigger approval
2. "Which card?" → Should trigger low confidence approval
3. "I'm spending ₹50,000 on flights" → Should NOT trigger approval
```

### Automated Testing

```python
# In evaluation/test_cases.json
{
  "id": "TC_HITL_001",
  "category": "hitl_high_value",
  "query": "I am spending ₹3,00,000 on flights",
  "expected_needs_approval": true,
  "expected_approval_reason": "high_value",
  "evaluation_criteria": {
    "approval_triggered": true
  }
}
```

---

## 📚 References

- [Human-in-the-Loop AI](https://en.wikipedia.org/wiki/Human-in-the-loop)
- [LangGraph Conditional Edges](https://python.langchain.com/docs/langgraph)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)

---

## ✅ Checklist

Before deploying HITL:

- [ ] Test all approval triggers
- [ ] Verify UI displays correctly
- [ ] Test all three actions (approve/reject/clarify)
- [ ] Check session state management
- [ ] Test with multiple users
- [ ] Add logging for approval decisions
- [ ] Document approval policies
- [ ] Train users on HITL workflow

---

**Built with ❤️ for IIT Madras Agentic AI Capstone**

**Last Updated**: July 2026
