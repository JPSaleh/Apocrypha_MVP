# Streamlit LLM Chatbot

A basic ChatGPT-like application built with Streamlit and OpenAI's API. This app demonstrates how to create a conversational chatbot with streaming responses.

## Features

- 🤖 Real-time chat interface
- 💬 Streaming responses for better user experience
- 🧠 Conversation history maintained in session state
- 🎨 Clean, modern UI with Streamlit's chat elements

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OpenAI API Key

1. Go to [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### 3. Configure API Key

Edit the `.streamlit/secrets.toml` file and replace `YOUR_API_KEY` with your actual OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## How It Works

- Uses `st.chat_message` to display chat messages with user and assistant avatars
- Uses `st.chat_input` to accept user input
- Maintains conversation history in `st.session_state`
- Streams responses from OpenAI's API for a more natural chat experience
- Uses the `gpt-3.5-turbo` model by default

## Reference

This app is based on the [Streamlit tutorial](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps) for building conversational apps.

## Notes

- Make sure to keep your API key secure and never commit it to version control
- The `.streamlit/secrets.toml` file is included in this repo for demonstration purposes - in production, use environment variables or Streamlit Cloud secrets management
- Consider adding error handling for API failures and rate limits
