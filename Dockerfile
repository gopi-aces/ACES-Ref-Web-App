# Use the official Python image as a base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the port that Streamlit uses (8501)
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "BibTeX-Web-App.py", "--server.port=8501", "--server.address=0.0.0.0"]
