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
            bib_content = st_ace(language='latex', theme='github', height=500)

            if st.button('Generate .bbl'):
                if bib_content:
                    # Save BibTeX content to a file using UTF-8 encoding
                    with open('temp.bib', 'w', encoding='utf-8') as f:
                        f.write(bib_content)

                    # LaTeX document content
                    tex_content = f"""
                    \\documentclass{{article}}
                    \\usepackage{{cite}}
                    \\usepackage{{hyperref}}
                    \\usepackage[utf8]{{inputenc}}
	                \\usepackage[T1]{{fontenc}}
	                \\usepackage{{amsmath,amssymb,amsfonts}}
                    \\begin{{document}}
                    \\cite{{*}}
                    \\bibliographystyle{{bst/{selected_bst}}}
                    \\bibliography{{temp}}
                    \\end{{document}}
                    """

                    # Save the .tex file using UTF-8 encoding
                    with open('testbib.tex', 'w', encoding='utf-8') as tex_file:
                        tex_file.write(tex_content)

                    # Docker command to run MiKTeX
                    docker_command = [
                        'docker', 'run', '--rm',
                        '-v', f"{os.getcwd()}:/miktex/work",
                        'miktex/miktex',
                        'pdflatex', 'testbib'
                    ]
                    bibtex_command = [
                        'docker', 'run', '--rm',
                        '-v', f"{os.getcwd()}:/miktex/work",
                        'miktex/miktex',
                        'bibtex', 'testbib'
                    ]

                    try:
                        # Run pdflatex and bibtex commands inside Docker
                        subprocess.run(docker_command, check=True)
                        subprocess.run(bibtex_command, check=True)
                        subprocess.run(docker_command, check=True)  # Run again for references

                        # Read the generated .bbl file using UTF-8 encoding
                        with open('testbib.bbl', 'r', encoding='utf-8') as bbl_file:
                            bbl_content = bbl_file.read()

                        st.subheader('Generated .bbl Content:')
                        st.markdown(f"```\n{bbl_content}\n```")
                    except subprocess.CalledProcessError as e:
                        # Show detailed error if LaTeX or BibTeX fails
                        with open('testbib.blg', 'r', encoding='utf-8') as log_file:
                            log_content = log_file.read()
                        st.error(f"An error occurred while running commands:\n{e}")
                        st.text("BibTeX Log Output:")
                        st.code(log_content)
                else:
                    st.warning("Please provide BibTeX content before generating the .bbl file.")

# Call the function to generate the page
generate_bbl_page()
