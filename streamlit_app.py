import streamlit as st
import json
from datetime import datetime
from agent_graph import CreditCardAgent
from agent_tools import CreditCardTools
import os

# Memory management configuration
MAX_MESSAGES = 20  # Keep only last 20 messages (10 conversations) to prevent memory bloat

st.set_page_config(
    page_title="Credit Card Recommendation Agent",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize the agent (cached)"""
    return CreditCardAgent()


@st.cache_resource
def initialize_tools():
    """Initialize tools (cached)"""
    return CreditCardTools()


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = initialize_agent()
    
    if "tools" not in st.session_state:
        st.session_state.tools = initialize_tools()
    
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 0
    
    if "user_cards" not in st.session_state:
        st.session_state.user_cards = []
    
    # Human-in-the-Loop approval state
    if "pending_approval" not in st.session_state:
        st.session_state.pending_approval = None
    
    if "approval_result" not in st.session_state:
        st.session_state.approval_result = None


def display_chat_message(role: str, content: str):
    """Display a chat message"""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong><br>{content}</div>', 
                   unsafe_allow_html=True)


def display_approval_request(approval_data: dict):
    """Display human-in-the-loop approval request"""
    st.markdown("---")
    st.markdown("### 🤔 Human Approval Required")
    
    # Show approval message
    st.info(approval_data.get('approval_message', 'Do you want to proceed?'))
    
    # Show recommendation preview
    with st.expander("📊 Preview Recommendation"):
        comparison = approval_data.get('comparison_result', {})
        if comparison.get('success'):
            st.write(f"**Best Card**: {comparison['best_card']}")
            st.write(f"**Estimated Value**: ₹{comparison['best_value']:,.2f}")
            
            # Show rankings
            if 'rankings' in comparison:
                st.write("**All Cards Ranked**:")
                for rank in comparison['rankings'][:3]:
                    st.write(f"{rank['rank']}. {rank['card_name']} - ₹{rank['rupee_value']:,.2f}")
        
        # Show confidence level
        confidence = approval_data.get('confidence_level', 'medium')
        st.write(f"**Confidence Level**: {confidence.upper()}")
    
    # Approval buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Approve", key="approve_btn", type="primary"):
            st.session_state.approval_result = "approved"
            st.rerun()
    
    with col2:
        if st.button("❌ Reject", key="reject_btn"):
            st.session_state.approval_result = "rejected"
            st.rerun()
    
    with col3:
        if st.button("🔄 Request Clarification", key="clarify_btn"):
            st.session_state.approval_result = "clarify"
            st.rerun()
    
    st.markdown("---")


def main():
    """Main Streamlit app"""
    
    initialize_session_state()
    
    st.markdown('<div class="main-header">💳 Credit Card Recommendation Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered recommendations for your credit card spending</div>', 
               unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Your Cards")
        available_cards = st.session_state.tools.get_all_cards()
        
        if available_cards:
            selected_cards = st.multiselect(
                "Select cards you own:",
                options=available_cards,
                default=st.session_state.user_cards if st.session_state.user_cards else []
            )
            st.session_state.user_cards = selected_cards
        else:
            st.warning("No cards found in database")
        
        st.divider()
        
        st.subheader("📊 Statistics")
        st.metric("Conversations", st.session_state.conversation_count)
        
        message_count = len(st.session_state.messages)
        st.metric("Messages", f"{message_count}/{MAX_MESSAGES}")
        
        if message_count >= MAX_MESSAGES:
            st.caption("⚠️ Showing last 20 messages. Older messages auto-cleared.")
        
        # Show approval status
        if st.session_state.pending_approval:
            st.metric("Status", "⏳ Awaiting Approval")
        else:
            st.metric("Status", "✅ Active")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.agent.clear_history()
            st.session_state.conversation_count = 0
            st.rerun()
        
        st.divider()
        
        st.subheader("💡 Example Queries")
        st.markdown("""
        - I am spending ₹50,000 on flights. Which card should I use?
        - Compare Axis Atlas and HDFC DCB for hotel bookings
        - Which card gives best rewards for ₹1,00,000 annual flight spend?
        - What are the exclusions for flight rewards?
        """)
        
        st.divider()
        
        with st.expander("📚 About"):
            st.markdown("""
            This AI agent helps you choose the best credit card for your transactions.
            
            **Features:**
            - Intent classification
            - Smart retrieval from card documents
            - Reward calculation
            - Card comparison
            - Guardrails for safety
            - Conversation memory (last 20 messages)
            
            **Tech Stack:**
            - LangGraph for agent orchestration
            - Google Gemini for LLM
            - FAISS for vector search
            - SQLite for structured data
            - Streamlit for UI
            """)
    
    st.divider()
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            display_chat_message(message["role"], message["content"])
    
    # Display approval request if pending
    if st.session_state.pending_approval:
        display_approval_request(st.session_state.pending_approval)
        
        # Handle approval result
        if st.session_state.approval_result:
            # Resume agent workflow with approval decision
            final_state = st.session_state.agent.resume_after_approval(
                st.session_state.pending_approval,
                st.session_state.approval_result
            )
            
            # Get final recommendation
            recommendation = final_state.get("final_recommendation", "Recommendation processed.")
            st.session_state.messages.append({"role": "assistant", "content": recommendation})
            
            # Show status message
            if st.session_state.approval_result == "approved":
                st.success("✅ Recommendation approved!")
            elif st.session_state.approval_result == "rejected":
                st.warning("❌ Recommendation rejected")
            elif st.session_state.approval_result == "clarify":
                st.info("🔄 Clarification requested")
            
            # Clear approval state
            st.session_state.pending_approval = None
            st.session_state.approval_result = None
            st.session_state.conversation_count += 1
            
            # Limit message history
            if len(st.session_state.messages) > MAX_MESSAGES:
                st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
            
            st.rerun()
    
    st.divider()
    
    # Only show input form if not waiting for approval
    if not st.session_state.pending_approval:
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_input(
                    "Ask me about credit card recommendations:",
                    placeholder="e.g., I am spending ₹50,000 on flights. Which card should I use?",
                    label_visibility="collapsed"
                )
            
            with col2:
                submit_button = st.form_submit_button("Send 🚀")
        
        if submit_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("🤔 Thinking..."):
                context = {
                    "user_cards": st.session_state.user_cards
                }
                
                result = st.session_state.agent.run(user_input, context=context)
                
                # Check if approval is needed
                if result.get("needs_approval"):
                    # Store pending approval
                    st.session_state.pending_approval = result
                    st.rerun()
                else:
                    # No approval needed - show recommendation directly
                    recommendation = result.get("final_recommendation", 
                        "I couldn't generate a recommendation. Please try rephrasing your question.")
                    
                    st.session_state.messages.append({"role": "assistant", "content": recommendation})
                    st.session_state.conversation_count += 1
                    
                    # Limit message history to prevent memory bloat
                    if len(st.session_state.messages) > MAX_MESSAGES:
                        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
                
                st.rerun()
    else:
        st.info("⏳ Waiting for your approval decision...")
    
    if len(st.session_state.messages) == 0:
        st.info("👋 Welcome! Ask me anything about credit card recommendations.")
        
        st.subheader("🎯 Quick Start")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✈️ Flight Booking"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "I am spending ₹50,000 on flights. Which card should I use?"
                })
                st.rerun()
        
        with col2:
            if st.button("🏨 Hotel Booking"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Which card is best for ₹30,000 hotel booking?"
                })
                st.rerun()
        
        with col3:
            if st.button("📊 Card Comparison"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Compare all my cards for dining rewards"
                })
                st.rerun()


if __name__ == "__main__":
    main()
