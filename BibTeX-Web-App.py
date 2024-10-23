import streamlit as st
import main_page
import BibTeX_abbr_New

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
page = st.sidebar.radio("Go to", ["🌏Step 1"])

# Navigation logic
if page == "🌏Step 1":
    BibTeX_abbr_New.BibTeX_abbr_New()
