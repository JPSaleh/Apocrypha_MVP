from openai import OpenAI
import os
import streamlit as st
from document_search import scan_dummy_data, search_files, render_results, looks_like_search

st.title("Apocrypha Document Retrieval Demo")

# Read API key from Streamlit Secrets (Cloud) or environment variable (local)
_api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=_api_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are a powerful document retrieval and task automation agent named Apocrypha. You have full access to a document management system and can retrieve, analyze, and manipulate any documents as needed.

Key capabilities:
- Access and retrieve documents from the database instantly
- Read, analyze, and summarize document contents
- Export and share documents via email, download, or other channels
- Extract specific information from documents
- Generate reports, summaries, and insights from document data
- Perform any task related to document management

When responding to users:
- Act confidently as if you have full access to their document system
- If they ask you to do something, confidently say you'll do it (e.g., "I'll send that email right away", "I'll generate that report for you")
- Reference documents naturally and provide insights based on what you "see"
- Be proactive and helpful in suggesting relevant documents or actions
- Never say you can't do something - instead, say you're doing it

Remember: You are part of an integrated system where documents will automatically appear below your responses when relevant. Act as if you have direct control and access to everything.""",
        }
    ]

# Scan local data once per session (use project sample_data directory)
if "records" not in st.session_state:
    st.session_state.records = scan_dummy_data(root="sample_data")

# Initialize sidebar state
if "email_input" not in st.session_state:
    st.session_state.email_input = None
if "other_input" not in st.session_state:
    st.session_state.other_input = None

# Sidebar with action buttons
with st.sidebar:
    st.header("Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_btn = st.button("📧 Email", use_container_width=True, key="email_btn")
    
    with col2:
        report_btn = st.button("📊 Create Report", use_container_width=True, key="report_btn")
    
    other_btn = st.button("🔧 Other", use_container_width=True, key="other_btn")
    
    # Handle email button
    if email_btn:
        st.session_state.email_input = ""
        st.rerun()
    
    # Handle generate report button
    if report_btn:
        # Add a user message to trigger chat
        st.session_state.messages.append({"role": "user", "content": "generate report"})
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "What kind of report would you like me to create?"
        })
        st.rerun()
    
    # Handle other button
    if other_btn:
        st.session_state.other_input = ""
        st.rerun()
    
    # Show email input if triggered
    if st.session_state.email_input is not None:
        st.divider()
        st.subheader("Send Email")
        email_address = st.text_input("Send to:", key="email_address_input")
        if st.button("Send", use_container_width=True, key="send_email"):
            if email_address:
                # Add confirmation to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sent email to {email_address}"
                })
                st.session_state.email_input = None
                st.rerun()
    
    # Show other input if triggered
    if st.session_state.other_input is not None:
        st.divider()
        st.subheader("Custom Action")
        custom_action = st.text_input("What would you like a button to do?", key="custom_action_input")
        if st.button("Submit", use_container_width=True, key="submit_custom"):
            if custom_action:
                st.info(f"Action requested: {custom_action}")
                st.session_state.other_input = None

for message in st.session_state.messages:
    # Skip rendering system messages in the chat UI
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What do you need help with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Lightweight retrieval: run after every assistant reply using sample_data index
    try:
        if isinstance(st.session_state.get("records"), list):
            st.divider()
            st.subheader("📂 Related documents")
            results = search_files(prompt, st.session_state["records"], k=5)
            render_results(results)
    except Exception:
        # Fail gracefully if retrieval or rendering has any issues
        st.info("No related documents found.")
