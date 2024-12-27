# Use the official MiKTeX image
FROM miktex/miktex:essential

# Install necessary LaTeX packages (optional)
RUN miktexsetup finish && mpm --admin --install=amsmath,hyperref

# Set up working directory in the container
WORKDIR /miktex/work

# Expose the application port (if required)
EXPOSE 8501

# Set the default command to run a shell
CMD ["/bin/bash"]
