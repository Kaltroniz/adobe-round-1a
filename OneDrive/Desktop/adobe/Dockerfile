# Use a lightweight, secure Python base image compatible with AMD64
FROM --platform=linux/amd64 python:3.9-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY src/ /app/src/

# Run the download script to cache the model files inside the image.
# This step MUST have internet access.
RUN python /app/src/download_model.py

# --- MOVED FROM THE TOP ---
# Now that all downloads are done, set the offline flag.
# This will apply to the final running container.
ENV TRANSFORMERS_OFFLINE=1

# Command to run when the container starts.
# It will now run in offline mode using the cached model.
CMD ["python", "src/main_1b.py"]