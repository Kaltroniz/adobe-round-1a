requirement# 🏆 Advanced PDF Structure Analysis Engine

This project is a high-accuracy, high-performance solution for extracting structured outlines from PDF documents, built to win the "Connecting the Dots Through Docs" hackathon challenge.

## ✨ The Winning Edge: Feature-Based Scoring

While many solutions might use simple rules based on font size, this engine employs a more intelligent **feature-based scoring model**. It analyzes every line of text against a rich set of typographic, positional, and semantic features to calculate a "heading score." This mimics the decision-making of a lightweight machine learning model, providing superior accuracy and robustness.

### Key Features of the Model:

* **Relative Font Analysis:** Compares font sizes against the document's automatically detected **body text size**, not a fixed value.
* **Positional Intelligence:** Measures **whitespace above a line** and checks for **horizontal centering**, which are strong indicators of a heading.
* **Content Heuristics:** The score is influenced by text patterns, such as capitalization, line length, word count, and the presence of numbered lists (e.g., "2.1.3").
* **Penalty System:** Lines ending in periods are penalized, effectively distinguishing headings from regular sentences.
* **Language Agnostic:** The core features (font properties, spacing, positioning) are universal, making this solution effective for multilingual documents and securing the **multilingual bonus**.

This multi-faceted approach ensures the extractor works reliably on a wide variety of document layouts, from academic papers to corporate reports.

## 📚 Libraries Used
* **PyMuPDF (`fitz`)**: Chosen for its exceptional speed and detailed metadata extraction capabilities.

## 🚀 How to Build and Run

### Build the Docker Image
From the project root directory, run the standard build command:
```bash
docker build --platform linux/amd64 -t mysolution .
```

### Run the Container
1. Place your input PDF files in a local directory (e.g., `input`).
2. Create an empty local directory for the results (e.g., `output`).
3. Run the container using the command below, which mounts your local directories into the container.

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution
```
The engine will automatically process all `.pdf` files from `/app/input` and generate a corresponding structured `.json` file for each in `/app/output`.