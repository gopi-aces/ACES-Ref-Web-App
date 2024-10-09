import streamlit as st
import openai
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import load_settings  # Import shared functions

# System message to define the assistant's role and BibTeX formatting guidelines
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are a reference formatting assistant specialized in converting academic references into the correct BibTeX format.

Please follow these guidelines:

1. Use the BibTeX format for each reference.
2. Start each entry with the correct BibTeX type (e.g., `@article`, `@book`, `@inbook`, `@incollection`, `@misc`, `@phdthesis`, `@inproceedings`, etc.).
3. Ensure that each reference follows this structure:

@article{reference_key, author = {Author Name and Another Author}, title = {Title of the Paper}, journal = {Abbrivated Journal Name}, year = {Year}, volume = {Volume}, number = {Issue Number}, pages = {Page Range}, doi = {DOI Number}, url = {URL if available} }

4. Separate multiple authors using the `and` keyword.
5. Skip empty fields, and exclude any missing information.
6. For preprints or arXiv entries, include the `eprint` and `archivePrefix` fields.
7. Abbrivated the Journal Names in '@article' type bibtex
8. Respond only with the BibTeX formatted output without any additional commentary or explanation.
"""
}

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

# Use LangChain Text Splitter to handle large inputs
def split_large_input(input_text, chunk_size=3000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(input_text)
    return chunks

# Function to dynamically manage tokens and trim conversation
def trim_conversation(conversation, max_tokens=14000):
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
    return [SYSTEM_MESSAGE] if len(history) > 1 else history  # Keep only the first message

def main_page_with_abbr():
    st.title('🚀 ACES BibTeX with Journal Abbreviation')

    # Load settings
    settings = load_settings()
    current_model = settings["model"]

    # File to save chat history
    history_file = 'chat_history_abbr.json'

    # Initialize chat session in Streamlit if not already present
    if "chat_history_abbr" not in st.session_state:
        st.session_state.chat_history_abbr = [SYSTEM_MESSAGE]  # Start with the system message

    # Button to delete all history except the first message
    if st.button("Delete All History Except First Message"):
        st.session_state.chat_history_abbr = keep_first_message(st.session_state.chat_history_abbr)
        save_history_to_file(st.session_state.chat_history_abbr, history_file)
        st.success("Chat history trimmed to keep only the first message.")

    # Display chat history, excluding the `system` role messages
    for message in st.session_state.chat_history_abbr:
        if message["role"] != "system":  # Exclude system messages from being displayed
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input field for user's message
    user_prompt = st.chat_input("👉 Enter your Refs...")

    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history_abbr.append({"role": "user", "content": user_prompt})

        # Split the input into small chunks using LangChain's text splitter
        input_chunks = split_large_input(user_prompt, chunk_size=3000, chunk_overlap=100)

        for chunk in input_chunks:
            # Add each chunk to the conversation history
            st.session_state.chat_history_abbr.append({"role": "user", "content": chunk})

            # Ensure the system message is the first message in the conversation
            st.session_state.chat_history_abbr = ensure_system_message(st.session_state.chat_history_abbr)

            # Trim conversation history to stay within limits
            st.session_state.chat_history_abbr = trim_conversation(st.session_state.chat_history_abbr, max_tokens=14000)

        setup_openai()
        try:
            with st.chat_message("assistant"):
                assistant_message_placeholder = st.empty()
                assistant_response_stream = ""

                # Ensure the system message is always included
                adjusted_history = ensure_system_message(st.session_state.chat_history_abbr)

                # Make the API call with streaming enabled
                response = openai.ChatCompletion.create(
                    model=current_model,
                    messages=adjusted_history,
                    stream=True  # Enable streaming
                )

                # Stream the response and display it progressively
                for chunk in response:
                    if "choices" in chunk:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            assistant_response_stream += delta["content"]

                # Display the full response as a single formatted code block with a "Copy" button
                assistant_message_placeholder.markdown(f"```bibtex\n{assistant_response_stream}\n```")

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