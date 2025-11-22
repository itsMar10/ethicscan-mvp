FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y build-essential

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies (including the heavy Spacy model)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]