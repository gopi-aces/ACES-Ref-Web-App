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
- 📘 **BibTeX Abbreviation**: Convert your academic references into the correct BibTeX format with journal abbreviations.
- 📄 **Generate BBL**: Generate `.bbl` files from your BibTeX entries using a `.bst` file.

Use the sidebar to navigate between the tools:
- Step 1: Convert references into BibTeX format.
- Step 2: Generate `.bbl` files for LaTeX documents.
""")

# Instructions for users
st.markdown("""
### How to Use:
1. **Navigate**: Use the sidebar on the left to select a page.
2. **Step 1**: Go to the **BibTeX Abbreviation** page to convert your references.
3. **Step 2**: Go to the **Generate BBL** page to create a `.bbl` file.
4. **Follow Instructions**: Each page contains instructions specific to that tool.
""")

st.sidebar.success("Select a page above to get started.")
