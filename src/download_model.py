# src/download_model.py

from sentence_transformers import SentenceTransformer

def main():
    """
    Downloads and caches the specified model from Hugging Face.
    This script is intended to be run during the Docker build process.
    """
    model_name = 'all-MiniLM-L6-v2'
    print(f"Downloading and caching model: {model_name}")
    
    # This line triggers the download and caches the model automatically
    SentenceTransformer(model_name)
    
    print("Model has been cached successfully.")

if __name__ == "__main__":
    main()