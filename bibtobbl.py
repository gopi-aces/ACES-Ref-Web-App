import streamlit as st
import os
import subprocess
from streamlit_ace import st_ace

def generate_bbl_page():
    st.title('BibTeX to BBL Converter')

    bst_folder = 'bst'
    if not os.path.exists(bst_folder):
        st.error(f"Folder '{bst_folder}' not found. Please create the folder and add .bst files.")
    else:
        bst_files = [f for f in os.listdir(bst_folder) if f.endswith('.bst')]
        if not bst_files:
            st.error("No .bst files found in the 'bst' folder.")
        else:
            selected_bst = st.selectbox('Choose a .bst file', bst_files)

            st.subheader('Paste your BibTeX content below:')
            bib_content = st_ace(language='latex', theme='github', height=200)

            if st.button('Generate .bbl'):
                if bib_content:
                    with open('temp.bib', 'w') as f:
                        f.write(bib_content)

                    tex_content = f"""
                    \\documentclass{{article}}

                    \\usepackage{{cite}}

                    \\begin{{document}}

                    pdflatex testbib.tex

                    \\cite{{*}}
                    \\bibliographystyle{{bst/{selected_bst}}}
                    \\bibliography{{temp}}

                    \\end{{document}}
                    """

                    with open('testbib.tex', 'w') as tex_file:
                        tex_file.write(tex_content)

                    pdflatex_command = ['pdflatex', 'testbib']
                    bibtex_command = ['bibtex', 'testbib']

                    try:
                        subprocess.run(pdflatex_command, check=True)
                        subprocess.run(bibtex_command, check=True)

                        with open('testbib.bbl', 'r') as bbl_file:
                            bbl_content = bbl_file.read()

                        st.subheader('Generated .bbl Content:')
                        st.markdown(f"```\n{bbl_content}\n```")
                    except subprocess.CalledProcessError as e:
                        st.error(f"An error occurred while running commands:\n{e}")
                else:
                    st.warning("Please paste BibTeX content before generating the .bbl file.")
