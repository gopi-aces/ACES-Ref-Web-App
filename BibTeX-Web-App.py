import streamlit as st
import main_page
import BibTeX_journal_abbr
import bibtobbl  # Import the new bibtobbl module

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚦Navigation")
page = st.sidebar.radio("Go to", ["🌏BibTeX without Journal Abbr", "💥BibTeX with Journal Abbr"])

# Navigation logic
if page == "🌏BibTeX without Journal Abbr":
    main_page.main_page()
elif page == "💥BibTeX with Journal Abbr":
    BibTeX_journal_abbr.main_page_with_abbr()
