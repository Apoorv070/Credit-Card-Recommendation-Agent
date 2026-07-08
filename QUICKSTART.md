# 🚀 Quick Start Guide - Phase 2 Agent

## Prerequisites Check ✅

Before starting, ensure you have completed Phase 1:
- ✓ `data/faiss_index.bin` exists
- ✓ `data/chunks_mapping.json` exists
- ✓ `database/credit_cards.db` exists
- ✓ `data/models/all-MiniLM-L6-v2/` exists
- ✓ `.env` file has `GOOGLE_API_KEY`

## Installation (5 minutes)

### Step 1: Install New Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langgraph` - Agent orchestration
- `langchain` - LLM framework
- `langchain-google-genai` - Google Gemini integration
- `streamlit` - Web UI
- `faiss-cpu` - Vector search (if not already installed)

### Step 2: Verify Installation

```bash
python test_agent.py
```

Expected output:
```
✓ GOOGLE_API_KEY found
✓ data/faiss_index.bin
✓ data/chunks_mapping.json
✓ database/credit_cards.db
✓ RAG retriever initialized
✓ Agent tools initialized
✓ Agent initialized
✅ ALL TESTS PASSED!
```

## Running the Agent (3 options)

### Option 1: Streamlit Web App (Recommended) 🌐

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Beautiful chat interface
- Conversation memory
- Card selection
- Quick start buttons
- Real-time responses

### Option 2: Command Line Test 💻

```bash
python agent_graph.py
```

This runs predefined test queries and shows the agent's responses.

### Option 3: Python Script 🐍

```python
from agent_graph import CreditCardAgent

agent = CreditCardAgent()

result = agent.run("I am spending ₹50,000 on flights. Which card should I use?")

print(result["final_recommendation"])
```

## Example Queries to Try

### 1. Single Transaction
```
I am spending ₹50,000 on flights. Which card should I use?
```

### 2. Card Comparison
```
Compare Axis Atlas and HDFC Diners Club Black for hotel bookings
```

### 3. Category Query
```
Which card gives best rewards for dining?
```

### 4. Monthly Optimization
```
I have ₹1,20,000 annual hotel spends and ₹80,000 flight spends. Which card should I get?
```

### 5. General Question
```
What are the exclusions for flight rewards on Axis Atlas?
```

## Understanding the Output

### Example Response Structure

```markdown
## 💳 Recommendation for ₹50,000 flights spend

### 🏆 Best Card: **Axis Atlas**
**Estimated Value: ₹2,500**

### 📊 Calculation Details:
- Reward Rate: 2.00 points per ₹
- Points Earned: 100,000
- Point Value (assumed): ₹0.50 per point
- ⚠️ **Monthly cap applied**: 100,000 points

### 📈 Card Comparison:
1. **Axis Atlas**: ₹2,500 (100,000 points)
2. **HDFC DCB**: ₹1,875 (75,000 points)
3. **SBI Cashback**: ₹1,000 (1,000 points)

### 📚 Evidence:
Retrieved 5 relevant card rules

### ⚠️ Important Notes:
- ⚠️ Monthly caps may apply - verify with card terms
- ⚠️ Exclusions may apply - verify merchant eligibility

### 🎯 Confidence: HIGH

---
*Always verify with official card terms before making decisions.*
```

## Streamlit UI Guide

### Main Interface

1. **Chat Area** (center)
   - Shows conversation history
   - User messages in blue
   - Agent responses in gray

2. **Input Box** (bottom)
   - Type your query
   - Click "Send 🚀" or press Enter

3. **Sidebar** (left)
   - **Your Cards**: Select which cards you own
   - **Statistics**: Conversation and message count
   - **Clear History**: Reset the chat
   - **Example Queries**: Quick start buttons
   - **About**: Tech stack info

### Quick Start Buttons

Click these for instant queries:
- **✈️ Flight Booking** - "I am spending ₹50,000 on flights"
- **🏨 Hotel Booking** - "Which card is best for ₹30,000 hotel booking?"
- **📊 Card Comparison** - "Compare all my cards for dining rewards"

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:**
```bash
# Check .env file
cat .env

# Should contain:
GOOGLE_API_KEY=AIzaSy...
```

### Issue: "No module named 'langgraph'"

**Solution:**
```bash
pip install langgraph langchain langchain-google-genai
```

### Issue: "FAISS index not found"

**Solution:**
You need to complete Phase 1 first:
```bash
python 1_setup_sqlite.py
python 2_chunk_pdfs.py
# Then run embedding creation in Colab
```

### Issue: "SSL Certificate Error"

**Solution:**
This project uses **local embeddings** to avoid SSL issues. Make sure:
- `data/models/all-MiniLM-L6-v2/` exists
- Using local FAISS index (not Pinecone)

### Issue: "No cards found in database"

**Solution:**
```bash
# Check if database has data
sqlite3 database/credit_cards.db "SELECT COUNT(*) FROM reward_rules;"

# Should return > 0
```

If 0, run:
```bash
python 1_setup_sqlite.py
```

### Issue: Streamlit shows blank page

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart the app
streamlit run streamlit_app.py
```

## Performance Tips

### For Faster Responses

1. **Reduce retrieval chunks**
   Edit `agent_nodes.py`:
   ```python
   top_k = 3  # Instead of 5
   ```

2. **Use specific card names**
   Instead of: "Which card should I use?"
   Try: "Should I use Axis Atlas for flights?"

3. **Provide all details upfront**
   Instead of: "I want to book flights"
   Try: "I am spending ₹50,000 on flights"

## Next Steps

### Customize Point Valuation

Edit `agent_tools.py`:
```python
point_value = 0.5  # Change to your preferred valuation
```

### Add More Cards

1. Add PDFs to `data/raw_pdfs/`
2. Add card data to `data/card_data.csv`
3. Re-run Phase 1 pipeline

### Modify Agent Behavior

Edit `agent_nodes.py` to customize:
- Intent classification prompts
- Clarification questions
- Guardrail checks
- Output formatting

## Architecture Overview

```
User Query (Streamlit)
    ↓
Intent Classification (Gemini)
    ↓
Clarification (if needed)
    ↓
Retrieval (FAISS + SQLite)
    ↓
Rule Validation
    ↓
Calculation (Tool)
    ↓
Comparison (Tool)
    ↓
Guardrails Check
    ↓
Approval Gate (if complex)
    ↓
Final Answer
    ↓
Display in Streamlit
```

## Files Created in Phase 2

- `agent_state.py` - State definition
- `agent_tools.py` - Retrieval and calculation tools
- `agent_nodes.py` - LangGraph node implementations
- `agent_graph.py` - LangGraph workflow
- `streamlit_app.py` - Web UI
- `test_agent.py` - System test script
- `README_PHASE2.md` - Full documentation
- `ARCHITECTURE.md` - Architecture details
- `QUICKSTART.md` - This file

## Support

For detailed documentation, see:
- `README_PHASE2.md` - Complete guide
- `ARCHITECTURE.md` - Technical architecture
- Phase 1 files for data pipeline

## What's Next? (Phase 3)

Future enhancements:
1. **Evaluation Framework** - Test accuracy and hallucination
2. **Human-in-the-Loop** - Approval workflows
3. **Monitoring** - LangSmith integration
4. **Point Transfer Routing** - Complex optimization
5. **Persistent Memory** - Store user preferences

---

**Ready to start?** Run:
```bash
streamlit run streamlit_app.py
```

🎉 **Enjoy your AI-powered credit card recommendation agent!**
