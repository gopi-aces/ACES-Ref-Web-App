import streamlit as st
import os
import subprocess
from streamlit_ace import st_ace

# Permanent directory for storing .bst, .tex, and .bib files
perm_dir = r'D:\aces-ref-am'
bst_folder = os.path.join(perm_dir, 'bst')

# Ensure the permanent directory exists, create if it doesn't
if not os.path.exists(perm_dir):
    os.makedirs(perm_dir)
if not os.path.exists(bst_folder):
    os.makedirs(bst_folder)

def download_bst_files():
    # Logic to download .bst files into the 'bst' folder if needed.
    pass  # Implement downloading logic if necessary

# Download .bst files into the 'bst' folder if not already present
download_bst_files()

def generate_bbl_page():
    st.title('ACES Reference Structure and Ordering')

    # List available .bst files from the 'bst' folder
    if not os.path.exists(bst_folder):
        st.error(f"Folder '{bst_folder}' not found. Please add .bst files.")
    else:
        bst_files = [f for f in os.listdir(bst_folder) if f.endswith('.bst')]
        if not bst_files:
            st.error("No .bst files found in the 'bst' folder. Please add .bst files to proceed.")
        else:
            selected_bst = st.selectbox('Choose a .bst file', bst_files)

            # Input area for .bib content using Ace Editor
            bib_content = st_ace(language='latex', theme='github', height=300)

            if st.button('Generate .bbl File'):
                if bib_content:
                    try:
                        temp_bib_path = os.path.join(perm_dir, 'temp.bib')
                        temp_tex_path = os.path.join(perm_dir, 'testbib.tex')
                        bst_file_path = os.path.join(bst_folder, selected_bst)

                        # Save the .bib content
                        with open(temp_bib_path, 'w') as f:
                            f.write(bib_content)

                        # Create the .tex file for processing the bibliography
                        tex_content = f"""
                        \\documentclass{{article}}
                        \\usepackage{{cite}}
                        \\begin{{document}}
                        \\cite{{*}}
                        \\bibliographystyle{{bst/{selected_bst}}}
                        \\bibliography{{temp}}
                        \\end{{document}}
                        """

                        with open(temp_tex_path, 'w') as f:
                            f.write(tex_content)

                        # Compile LaTeX and BibTeX to generate the .bbl file
                        commands = [
                            ['pdflatex', 'testbib'],
                            ['bibtex', 'testbib']
                        ]
                        for cmd in commands:
                            subprocess.run(cmd, cwd=perm_dir, check=True)

                        temp_bbl_path = os.path.join(perm_dir, 'testbib.bbl')
                        if os.path.exists(temp_bbl_path):
                            # Read and display the generated .bbl file
                            with open(temp_bbl_path, 'r') as f:
                                bbl_content = f.read()
                            st.subheader('Generated .bbl File:')
                            st.code(bbl_content, language='')
                        else:
                            st.error("The .bbl file was not generated.")
                    except subprocess.CalledProcessError as e:
                        st.error(f"An error occurred during LaTeX compilation:\n{e}")

# Call the function to generate the page
generate_bbl_page()
