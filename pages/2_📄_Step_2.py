# bibtobbl.py
import streamlit as st
import os
import subprocess
from streamlit_ace import st_ace

def generate_bbl_page():
    st.title('References Order')

    # Define filenames used for logs and auxiliary files
    tex_file = 'testbib.tex'
    log_file = 'testbib.log'
    aux_file = 'testbib.aux'
    bbl_file = 'testbib.bbl'
    bib_file = 'temp.bib'
    blg_file = 'testbib.blg'

    # Docker-specific paths for accessing files inside the container
    container_work_dir = '/miktex/work/'

    # Add a button to clear only the log and aux files from the miktex-container
    if st.button('Clear .log and .aux Files'):
        clear_command = [
            'docker', 'exec', 'miktex-container',
            'sh', '-c', f'rm -f {container_work_dir}{log_file} {container_work_dir}{aux_file}'
        ]
        try:
            subprocess.run(clear_command, check=True)
            st.success(".log and .aux files have been deleted successfully from miktex-container!")
        except subprocess.CalledProcessError as e:
            st.error(f"Failed to delete .log and .aux files from miktex-container:\n{e}")

    # Display the main interface for BibTeX to BBL conversion
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

            if st.button('Generate Ref.'):
                if bib_content:
                    # Save BibTeX content to a .bib file using UTF-8 encoding
                    with open(bib_file, 'w', encoding='utf-8') as f:
                        f.write(bib_content)

                    # Create LaTeX document content
                    tex_content = f"""
                    \\documentclass{{article}}
                    \\usepackage{{cite}}
                    \\usepackage{{hyperref}}
                    \\usepackage[utf8]{{inputenc}}
                    \\usepackage[T1]{{fontenc}}
                    \\usepackage{{amsmath,amssymb,amsfonts}}
                    \\begin{{document}}
                    \\nocite{{*}}
                    \\bibliographystyle{{bst/{selected_bst}}}
                    \\bibliography{{temp}}
                    \\end{{document}}
                    """

                    # Save the .tex file using UTF-8 encoding
                    with open(tex_file, 'w', encoding='utf-8') as tex_file_obj:
                        tex_file_obj.write(tex_content)

                    # Docker commands for LaTeX and BibTeX execution
                    docker_pdflatex_command = [
                        'docker', 'exec', 'miktex-container',
                        'latex', f'{container_work_dir}{tex_file}'
                    ]

                    docker_bibtex_command = [
                        'docker', 'exec', 'miktex-container',
                        'bibtex', f'{container_work_dir}{tex_file[:-4]}'  # Remove .tex extension for BibTeX
                    ]

                    def run_command(command, description):
                        """Run a Docker command inside the miktex-container and show real-time output."""
                        st.info(f"Running: {description}")
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        for line in process.stdout:
                            st.text(line.strip())
                        process.wait()
                        return process.returncode

                    try:
                        # Run pdflatex -> bibtex -> pdflatex for complete compilation
                        if run_command(docker_pdflatex_command, "pdflatex (1st pass)") != 0:
                            st.error("First pass of pdflatex failed. Check the logs for details.")
                            return

                        if run_command(docker_bibtex_command, "bibtex") != 0:
                            st.error("BibTeX command failed. Check the logs for details.")
                            return

                        # Read and display the generated .bbl content
                        if os.path.exists(bbl_file):
                            with open(bbl_file, 'r', encoding='utf-8') as bbl_file_obj:
                                bbl_content = bbl_file_obj.read()
                            st.subheader('Generated Ref. Content:')
                            st.markdown(f"```bibtex\n{bbl_content}\n```")
                        else:
                            st.error("The .bbl file was not generated. Please check the logs for errors.")

                    except subprocess.CalledProcessError as e:
                        st.error(f"An error occurred while running Docker LaTeX commands:\n{e}")
                else:
                    st.warning("Please provide BibTeX content before generating the .bbl file.")

# Call the function to generate the page
generate_bbl_page()
