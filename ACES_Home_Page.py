import streamlit as st

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """


st.markdown(hide_st_style, unsafe_allow_html=True)

# Main page title and description
st.title("Welcome to the ACES Reference Tool")
st.markdown("""
This tool helps you format and manage academic references effortlessly.

### Features:
- Step 1: Convert references into Tag format.
- Step 2: Generate WS style References.
""")


st.sidebar.success("Select a page above to get started.")
