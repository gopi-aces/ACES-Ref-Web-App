# BibTeX_abbr.py
import streamlit as st
import openai
from utils import load_settings, save_settings  # Import shared functions

# Function to setup OpenAI API
def setup_openai():
    openai.api_key = st.secrets["OPENAI_API_KEY"]

def settings_page():
    st.title('⚙️Settings')

    # Load settings
    settings = load_settings()
    current_model = settings["model"]

    # Input field for updating the model
    new_model = st.text_input("Enter the model name:", value=current_model)

    if st.button("Save Model"):
        settings["model"] = new_model
        save_settings(settings)
        st.success(f"Model updated to {new_model}")

if __name__ == "__main__":
    settings_page()
