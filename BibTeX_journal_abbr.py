# BibTeX_journal_abbr.py
import streamlit as st
import openai
import json
import os
from utils import load_settings  # Import shared functions

# Function to setup OpenAI API
def setup_openai():
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to save the chat history to a file
def save_history_to_file(history, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Function to load the chat history from a file
def load_history_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Function to estimate the token count (average approx: 1 word = 1.33 tokens)
def estimate_token_count(text):
    return len(text.split())

# Function to trim the conversation to avoid exceeding token limits
def trim_conversation(conversation, max_tokens=4000):
    total_tokens = sum([estimate_token_count(msg['content']) for msg in conversation])
    trimmed_conversation = conversation[:]

    while total_tokens > max_tokens and len(trimmed_conversation) > 1:
        total_tokens -= estimate_token_count(trimmed_conversation.pop(0)['content'])
    return trimmed_conversation

# Function to split a large input into smaller chunks based on a delimiter
def split_large_input(input_text, delimiter="\n", max_tokens=3000):
    input_parts = input_text.split(delimiter)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for part in input_parts:
        part_token_count = estimate_token_count(part)
        if current_token_count + part_token_count < max_tokens:
            current_chunk.append(part)
            current_token_count += part_token_count
        else:
            chunks.append(delimiter.join(current_chunk))
            current_chunk = [part]
            current_token_count = part_token_count

    # Add any remaining parts as the last chunk
    if current_chunk:
        chunks.append(delimiter.join(current_chunk))

    return chunks

# Function to keep only the last 5 messages in chat history
def keep_last_n_messages(history, n=20):
    return history[-n:]

def main_page_with_abbr():
    st.title('🚀 ACES BibTeX with Journal Abbreviation')

    # Load settings
    settings = load_settings()
    current_model = settings["model"]

    # File to save chat history
    history_file = 'chat_history_abbr.json'

    # Initialize chat session in Streamlit if not already present
    if "chat_history_abbr" not in st.session_state:
        st.session_state.chat_history_abbr = load_history_from_file(history_file)

    # Button to delete all history except the last 5 chats
    if st.button("Delete All History Except Last 5"):
        st.session_state.chat_history_abbr = keep_last_n_messages(st.session_state.chat_history_abbr, 20)
        save_history_to_file(st.session_state.chat_history_abbr, history_file)
        st.success("Chat history trimmed to the last 5 messages.")

    # Display chat history
    for message in st.session_state.chat_history_abbr:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for user's message
    user_prompt = st.chat_input("👉 Enter your Refs...")

    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history_abbr.append({"role": "user", "content": user_prompt})

        # Split the input using a newline as the delimiter
        input_chunks = split_large_input(user_prompt, delimiter="\n", max_tokens=3000)

        for chunk in input_chunks:
            # Add chunk to the conversation and display it
            st.session_state.chat_history_abbr.append({"role": "user", "content": chunk})

            # Trim conversation history to stay within token limits
            st.session_state.chat_history_abbr = trim_conversation(st.session_state.chat_history_abbr, max_tokens=4000)

        # Send user's message to GPT-3.5-turbo and get a streamed response
        setup_openai()
        try:
            with st.chat_message("assistant"):
                assistant_message_placeholder = st.empty()
                assistant_response_stream = ""

                response = openai.ChatCompletion.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": "You are an assistant trained to convert academic references into BibTeX format with journal abbreviations."},
                        *st.session_state.chat_history_abbr
                    ],
                    stream=True  # Enable streaming
                )

                # Stream the response and display it progressively
                for chunk in response:
                    if "choices" in chunk:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            assistant_response_stream += delta["content"]
                            assistant_message_placeholder.markdown(assistant_response_stream)

                # Add the final assistant response to chat history
                st.session_state.chat_history_abbr.append({"role": "assistant", "content": assistant_response_stream})

                # Save the updated chat history
                save_history_to_file(st.session_state.chat_history_abbr, history_file)

        except openai.error.InvalidRequestError as e:
            st.error(f"Invalid request error: {e}")
        except openai.error.OpenAIError as e:
            st.error(f"OpenAI error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main_page_with_abbr()
