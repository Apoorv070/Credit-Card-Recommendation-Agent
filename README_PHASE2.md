# Credit Card Recommendation Agent - Phase 2

## 🎯 Overview

An AI-powered agent that helps users choose the best credit card for their transactions using **LangGraph** for agent orchestration, **Google Gemini** for LLM capabilities, and **RAG** (Retrieval Augmented Generation) for grounded recommendations.

## 🏗️ Architecture

### Agent Flow (LangGraph)

```
User Query (Streamlit UI)
    ↓
Node 1: Intent Classification
    ↓
Node 2: Clarification (if needed)
    ↓
Node 3: Retrieval (FAISS + SQLite)
    ↓
Node 4: Rule Validation
    ↓
Node 5: Calculation (Reward Calculator)
    ↓
Node 6: Comparison (Card Ranking)
    ↓
Node 7: Guardrails Check
    ↓
Node 8: Approval Gate (for complex queries)
    ↓
Node 9: Final Answer
    ↓
Streamlit UI Display
```

### Key Components

1. **`agent_state.py`** - Defines the state structure for LangGraph
2. **`agent_tools.py`** - Tools for retrieval, calculation, and comparison
3. **`agent_nodes.py`** - Individual node implementations
4. **`agent_graph.py`** - LangGraph workflow orchestration
5. **`streamlit_app.py`** - User interface with chat and memory
6. **`local_rag_retriever.py`** - RAG retrieval (Phase 1)

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Google API Key (Gemini)
- Completed Phase 1 (data ingestion and retrieval)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Verify Environment Variables

Make sure your `.env` file contains:

```
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_key (optional)
PINECONE_INDEX_NAME=credit-cards (optional)
```

### Step 3: Verify Data Files

Ensure these files exist from Phase 1:
- `data/faiss_index.bin` - FAISS vector index
- `data/chunks_mapping.json` - Chunk metadata
- `database/credit_cards.db` - SQLite database with reward rules
- `data/models/all-MiniLM-L6-v2/` - Local embedding model

### Step 4: Test the Agent (CLI)

```bash
python agent_graph.py
```

This will run test queries and verify the agent works.

### Step 5: Launch Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage Examples

### Example 1: Single Transaction

**User Query:**
```
I am spending ₹50,000 on flights. Which card should I use?
```

**Agent Response:**
- Classifies intent as "single_transaction"
- Retrieves flight reward rules from all cards
- Calculates rewards for each card
- Compares and recommends the best card
- Shows calculation breakdown with caps and exclusions

### Example 2: Card Comparison

**User Query:**
```
Compare Axis Atlas and HDFC Diners Club Black for hotel bookings
```

**Agent Response:**
- Retrieves hotel reward rules for both cards
- Calculates expected rewards
- Provides side-by-side comparison
- Mentions any caps or exclusions

### Example 3: Monthly Optimization

**User Query:**
```
I have ₹1,20,000 annual hotel spends and ₹80,000 flight spends. Which card should I get?
```

**Agent Response:**
- Classifies as "monthly_optimization"
- May ask for clarification on monthly breakdown
- Calculates total annual rewards for each card
- Recommends best card for this spend pattern

## 🧠 Agent Features

### 1. Intent Classification
- Single transaction recommendation
- Monthly spend optimization
- Point transfer strategy
- Card comparison
- General queries

### 2. Smart Clarification
- Asks for missing information (amount, category)
- Validates user input
- Guides conversation flow

### 3. Hybrid Retrieval
- **Vector Search (FAISS)**: Retrieves relevant context chunks from card documents
- **Structured Query (SQLite)**: Fetches exact reward rules and rates

### 4. Rule Validation
- Checks if retrieved rules are sufficient
- Sets confidence level (high/medium/low)
- Prevents hallucination by requiring evidence

### 5. Reward Calculation
- Calculates points/cashback for each card
- Applies monthly caps
- Checks exclusions
- Converts points to rupee value

### 6. Card Comparison
- Ranks cards by estimated value
- Shows detailed breakdown
- Highlights capped vs uncapped rewards

### 7. Guardrails
- Verifies retrieved evidence is used
- Checks if caps are mentioned
- Warns about exclusions
- Sets appropriate confidence levels
- Prevents invented rules

### 8. Approval Gate
- Requires confirmation for complex strategies (point transfers)
- Asks user approval for low-confidence recommendations

### 9. Memory & Context
- Maintains conversation history
- Tracks user's owned cards
- Remembers previous queries in session

## 📊 Streamlit UI Features

### Main Chat Interface
- Clean, modern chat UI
- Message history
- Real-time agent responses

### Sidebar
- **Card Selection**: Select which cards you own
- **Statistics**: Conversation count, message count
- **Clear History**: Reset conversation
- **Example Queries**: Quick start buttons
- **About Section**: Tech stack and features

### Quick Start Buttons
- Flight Booking query
- Hotel Booking query
- Card Comparison query

## 🔧 Configuration

### Point Valuation
Default point value is set to ₹0.5 per point in `agent_tools.py`:

```python
point_value = 0.5  # Modify this based on your valuation
```

### Retrieval Settings
Adjust in `agent_nodes.py`:

```python
top_k = 5  # Number of chunks to retrieve
```

### Confidence Thresholds
Defined in `agent_state.py`:

```python
CONFIDENCE_LEVELS = {
    "high": "Strong evidence from retrieved rules",
    "medium": "Some assumptions made",
    "low": "Limited evidence"
}
```

## 🗂️ Project Structure

```
CapstoneProject/
├── agent_state.py           # LangGraph state definition
├── agent_tools.py           # Retrieval and calculation tools
├── agent_nodes.py           # Individual node implementations
├── agent_graph.py           # LangGraph workflow
├── streamlit_app.py         # Streamlit UI
├── local_rag_retriever.py   # RAG retrieval (Phase 1)
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── data/
│   ├── faiss_index.bin      # Vector index
│   ├── chunks_mapping.json  # Chunk metadata
│   ├── card_data.csv        # Card data
│   └── models/              # Local embedding model
└── database/
    └── credit_cards.db      # SQLite database
```

## 🧪 Testing

### Test Agent CLI
```bash
python agent_graph.py
```

### Test Individual Components
```bash
# Test retrieval
python local_rag_retriever.py

# Test tools
python agent_tools.py
```

### Test Streamlit App
```bash
streamlit run streamlit_app.py
```

## 🔍 Debugging

### Enable Verbose Logging

In `agent_nodes.py`, add print statements:

```python
print(f"Intent: {state['intent']}")
print(f"Retrieved: {state['retrieved_context']}")
```

### Check State at Each Node

In `agent_graph.py`, add:

```python
for step in result:
    print(f"Step: {step}")
```

## 🚧 Known Limitations

1. **Point Valuation**: Uses fixed ₹0.5 per point (should be dynamic based on transfer partners)
2. **Monthly Caps**: Assumes caps reset monthly (doesn't track user's current usage)
3. **Exclusions**: Shows exclusions but doesn't validate merchant eligibility
4. **Transfer Partners**: Point transfer routing not yet implemented
5. **User Profiles**: Basic user card tracking (no persistent storage)

## 🔮 Future Enhancements (Phase 3)

1. **Evaluation Framework**
   - Test dataset with ground truth
   - Metrics: accuracy, hallucination rate, retrieval quality
   
2. **Human-in-the-Loop**
   - Approval workflow for complex recommendations
   - Feedback collection
   - Continuous learning

3. **Monitoring**
   - LangSmith integration
   - Query analytics
   - Error tracking
   - Performance metrics

4. **Advanced Features**
   - Point transfer routing
   - Multi-card optimization
   - Annual fee amortization
   - Milestone tracking
   - Dynamic point valuation

## 📝 Notes

- All calculations use **offline mode** (local embeddings, no external API calls for embeddings)
- Google Gemini is used only for intent classification and reasoning
- RAG retrieval ensures grounded recommendations (no hallucination)
- Guardrails prevent the agent from inventing card rules

## 🤝 Contributing

This is a capstone project. For questions or improvements, refer to the project documentation.

## 📄 License

Educational project - IIT Madras Agentic AI Capstone

---

**Built with:** LangGraph • Google Gemini • FAISS • SQLite • Streamlit • Sentence Transformers
