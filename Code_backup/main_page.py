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

# Estimate token count (approx: 1 word = 1.33 tokens)
def estimate_token_count(text):
    return len(text.split())  # Rough token estimate

# Function to dynamically manage tokens and trim conversation
def dynamic_trim_conversation(conversation, max_tokens=13000):
    """
    Aggressively trims the conversation history to fit within the max token count.
    Returns the trimmed conversation.
    """
    total_tokens = sum([estimate_token_count(msg['content']) for msg in conversation])
    trimmed_conversation = conversation[:]

    # Aggressively remove messages until we have enough room
    while total_tokens > max_tokens and len(trimmed_conversation) > 1:
        total_tokens -= estimate_token_count(trimmed_conversation.pop(0)['content'])

    return trimmed_conversation

# Split large inputs into smaller chunks
def split_large_input(input_text, max_tokens=4000):
    """
    Split large text input into smaller chunks based on the token count.
    """
    chunks = []
    current_chunk = []
    current_token_count = 0

    # Split based on characters to create better chunks
    for char in input_text:
        if current_token_count + 1 < max_tokens:
            current_chunk.append(char)
            current_token_count += 1
        else:
            # Save the chunk and reset
            chunks.append("".join(current_chunk))
            current_chunk = [char]
            current_token_count = 1

    if current_chunk:
        chunks.append("".join(current_chunk))

    return chunks

# Keep only the last n messages
def keep_last_n_messages(history, n=1):
    return history[-n:]

def main_page():
    st.title('✍ ACES Bibliography Management System')

    # Load settings
    settings = load_settings()
    current_model = settings["model"]

    # File to save chat history
    history_file = 'chat_history_main.json'

    # Initialize chat session in Streamlit if not already present
    if "chat_history_main" not in st.session_state:
        st.session_state.chat_history_main = load_history_from_file(history_file)

    # Button to delete all history except the last 1 message
    if st.button("Delete All History Except Last Message"):
        st.session_state.chat_history_main = keep_last_n_messages(st.session_state.chat_history_main, 1)
        save_history_to_file(st.session_state.chat_history_main, history_file)
        st.success("Chat history trimmed to the last message.")

    # Display chat history
    for message in st.session_state.chat_history_main:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for user's message
    user_prompt = st.chat_input("👉 Enter your Refs...")

    if user_prompt:
        # Split the input into small chunks for large text
        input_chunks = split_large_input(user_prompt, max_tokens=4000)

        for chunk in input_chunks:
            # Add each chunk to the conversation history
            st.session_state.chat_history_main.append({"role": "user", "content": chunk})

            # Dynamic trimming of conversation history to stay within limits
            st.session_state.chat_history_main = dynamic_trim_conversation(st.session_state.chat_history_main, max_tokens=13000)

            # Streamed output logic
            setup_openai()
            try:
                trimmed_history = dynamic_trim_conversation(st.session_state.chat_history_main, max_tokens=13000)

                with st.chat_message("assistant"):
                    assistant_message_placeholder = st.empty()
                    assistant_response_stream = ""

                    # Calculate available tokens for the assistant's response
                    available_tokens = 16385 - sum(estimate_token_count(msg['content']) for msg in trimmed_history)

                    # Adjust the history to fit the response within the token limit
                    if available_tokens < 3000:
                        # Trim the history further if needed
                        trimmed_history = keep_last_n_messages(trimmed_history, n=1)

                    # Make the API call with the adjusted history
                    response = openai.ChatCompletion.create(
                        model=current_model,
                        messages=[
                            {"role": "system",
                             "content": "You are an assistant trained to convert academic references into BibTeX format."},
                            *trimmed_history
                        ],
                        stream=True
                    )

                    for chunk in response:
                        if "choices" in chunk:
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                assistant_response_stream += delta["content"]
                                assistant_message_placeholder.markdown(assistant_response_stream)

                    # Add the assistant's response to chat history
                    st.session_state.chat_history_main.append(
                        {"role": "assistant", "content": assistant_response_stream})

                    save_history_to_file(st.session_state.chat_history_main, history_file)

            except openai.error.InvalidRequestError as e:
                st.error(f"Invalid request error: {e}")
            except openai.error.OpenAIError as e:
                st.error(f"OpenAI error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main_page()
