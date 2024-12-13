# Use a lightweight base image for Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files first to leverage Docker caching
COPY requirements.txt ./

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

RUN pip install sentence-transformers

# Copy the rest of the application
COPY . /app

# Define the entrypoint
CMD ["streamlit", "run", "run.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]
