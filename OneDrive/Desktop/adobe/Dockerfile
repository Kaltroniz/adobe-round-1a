# Use a lightweight, secure Python base image compatible with AMD64
FROM --platform=linux/amd64 python:3.9-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ .

# Command to run when the container starts
CMD ["python", "main.py"]