# Connecting the Dots Challenge - Round 1A Solution

This project is a solution for Round 1A of the "Connecting the Dots" Challenge. Its purpose is to take a raw PDF file as input and extract a structured outline, identifying the document's title and all primary (H1), secondary (H2), and tertiary (H3) headings.

The solution is packaged in a lightweight, offline Docker container that meets all competition requirements for performance and resource usage.

---
## Methodology and Approach

The core of this solution is a sophisticated heuristic-based model that does not rely on machine learning, ensuring fast execution and a small footprint. The process is as follows:

### 1. Text and Feature Extraction
First, the input PDF is processed using the **PyMuPDF (`fitz`)** library. The code iterates through the document line by line, extracting not just the text but also crucial stylistic features for each line:
* Font Size
* Font Weight (i.e., is it **bold**?)
* Page Number

Headers and footers are programmatically ignored to reduce noise.

### 2. Body Text Identification
To understand what a "heading" is, we first must understand what it is not. The algorithm analyzes all extracted text to find the most frequently occurring style (combination of font size and weight). This dominant style is designated as the document's main **body text**.

### 3. Heuristic Heading Scoring
Each line of text is then assigned a "heading score" based on a set of rules:
* **Size Contrast:** Lines with a font size larger than the body text receive a higher score.
* **Weight Emphasis:** Bolded text receives a score bonus, especially if the body text is not bold.
* **Conciseness:** Shorter lines with fewer words are more likely to be headings and get a higher score.
* **Layout Cues:** A line is only considered a potential heading if it is followed by a line of text with a smaller font size. This is a critical rule to differentiate headings from other incidental large text.

### 4. Style Classification (H1, H2, H3)
Any text style whose lines consistently achieve a score above a set threshold (`min_score_threshold`) is classified as a heading style. These heading styles are then sorted by font size in descending order:
* The largest font size is mapped to **H1**.
* The second largest is mapped to **H2**.
* All other qualifying styles are mapped to **H3**.

### 5. Title Extraction
The document title is identified separately by finding the text with the largest font size on the first page. This is then excluded from the main outline to avoid duplication.

The final output is a clean JSON file containing the extracted title and a hierarchically sorted list of headings.

---
## Libraries Used

* **Python 3.9**: The core programming language.
* **PyMuPDF (`fitz`)**: Used for all PDF parsing and extraction of text and style information.

---
## How to Build and Run the Solution

The solution is fully containerized with Docker.

### Prerequisites

* Docker Desktop installed and running.

### 1. Prepare Your Project
Ensure your project structure is as follows:
your_project_folder/
├── src/
│   ├── advanced_processor.py   # Your class for processing PDFs
│   └── main.py                 # Your main script that uses the class
├── Dockerfile
└── requirements.txt

Your `requirements.txt` should contain:

PyMuPDF

2. Build the Docker Image
Open a terminal in the project's root directory and run the build command:

Bash

docker build -t solution1a:latest .
3. Run the Solution
Create an input directory and place your PDF file(s) inside it.

Create an empty output directory.

Execute the run command below. It processes all PDFs from /app/input and generates a corresponding .json file for each in /app/output.

For Windows (CMD):

DOS

docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" --network none solution1a:latest
For Linux / macOS / PowerShell:

Bash

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none solution1a:
