import streamlit as st
import openai
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import load_settings  # Import shared functions

# System message for context
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a reference formatting assistant specialized in converting academic references into the correct BibTeX format with journal abbreviations."
}

# Function to set up OpenAI API Key
def setup_openai():
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to save chat history to a file
def save_history_to_file(history, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Function to load chat history from a file
def load_history_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [SYSTEM_MESSAGE]  # Start with the system message if no history is found

# Function to estimate token count based on text length
def estimate_token_count(text):
    return len(text.split())  # Rough token estimate

# Use LangChain Text Splitter for efficient chunking of large inputs
def split_large_input(input_text, chunk_size=3000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(input_text)
    return chunks

# Function to trim conversation to fit within token limits
def trim_conversation(conversation, max_tokens=15000):
    total_tokens = sum([estimate_token_count(msg['content']) for msg in conversation])
    trimmed_conversation = conversation[:]

    while total_tokens > max_tokens and len(trimmed_conversation) > 1:
        total_tokens -= estimate_token_count(trimmed_conversation.pop(0)['content'])
    return trimmed_conversation

# Function to ensure the system message is always the first in the conversation
def ensure_system_message(conversation):
    if len(conversation) == 0 or conversation[0]["role"] != "system":
        return [SYSTEM_MESSAGE] + conversation
    return conversation

# Function to keep only the first message in chat history
def keep_first_message(history):
    return [SYSTEM_MESSAGE] if len(history) > 1 else history  # Keep only the system message

def BibTeX_abbr_New():
    st.title('✍️ ACES BibTeX with Journal Abbreviation')

    # Load settings from external configuration
    settings = load_settings()
    current_model = settings["model"]

    # Define file to save chat history
    history_file = 'chat_history_abbr1.json'

    # Initialize chat session if not present
    if "chat_history_abbr" not in st.session_state:
        st.session_state.chat_history_abbr = load_history_from_file(history_file)

    # Ensure system message is always the first message in history
    st.session_state.chat_history_abbr = ensure_system_message(st.session_state.chat_history_abbr)

    # Button to delete all history except the first message
    if st.button("Delete All History Except First Message"):
        st.session_state.chat_history_abbr = keep_first_message(st.session_state.chat_history_abbr)
        save_history_to_file(st.session_state.chat_history_abbr, history_file)
        st.success("Chat history trimmed to keep only the first message.")

    # Display chat history, excluding `system` role messages
    for message in st.session_state.chat_history_abbr:
        if message["role"] != "system":  # Exclude system messages from display
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input field for user's message
    user_prompt = st.chat_input("👉 Enter your Refs...")

    if user_prompt:
        # Add user's message to chat history and display it
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history_abbr.append({"role": "user", "content": user_prompt})

        # Split the input into chunks using LangChain's text splitter
        input_chunks = split_large_input(user_prompt, chunk_size=3000, chunk_overlap=100)

        # Set up OpenAI API key
        setup_openai()
        try:
            combined_response = ""  # Initialize an empty string to store the combined response

            # Iterate over each chunk and process with the OpenAI API
            for chunk in input_chunks:
                # Ensure the system message is always the first in the conversation
                st.session_state.chat_history_abbr = ensure_system_message(st.session_state.chat_history_abbr)

                # Trim conversation history to stay within limits
                st.session_state.chat_history_abbr = trim_conversation(st.session_state.chat_history_abbr, max_tokens=15000)

                # Make the API call with streaming enabled
                response = openai.ChatCompletion.create(
                    model=current_model,
                    messages=st.session_state.chat_history_abbr + [{"role": "user", "content": chunk}],
                    stream=True  # Enable streaming
                )

                # Stream the response and append to the combined response
                assistant_response_stream = ""
                for chunk in response:
                    if "choices" in chunk:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            assistant_response_stream += delta["content"]

                combined_response += assistant_response_stream  # Add the response for this chunk to the combined response

            # Display the combined response as a single formatted code block with a "Copy" button
            with st.chat_message("assistant"):
                st.markdown(f"```bibtex\n{combined_response}\n```")

            # Add the final combined assistant response to chat history
            st.session_state.chat_history_abbr.append({"role": "assistant", "content": combined_response})

            # Save the updated chat history
            save_history_to_file(st.session_state.chat_history_abbr, history_file)

        except openai.error.InvalidRequestError as e:
            st.error(f"Invalid request error: {e}")
        except openai.error.OpenAIError as e:
            st.error(f"OpenAI error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    BibTeX_abbr_New()
