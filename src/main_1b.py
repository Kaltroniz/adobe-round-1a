import json
import time
from pathlib import Path
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import torch
import re

# Import your class from the other file
from advanced_processor import AdvancedPDFProcessor

# --- Helper Function to get section content ---
def extract_text_for_sections(doc: fitz.Document, outline: list) -> list:
    """
    Extracts the full text content for each section defined in the outline.
    This function pairs each heading with its corresponding text content.
    """
    # Add a dummy heading at the end to correctly capture the last section's content
    end_marker = {'page': len(doc), 'text': 'End of Document'}
    outline_with_end = outline + [end_marker]
    
    sections_with_content = []
    
    for i in range(len(outline_with_end) - 1):
        current_heading = outline[i]
        next_heading = outline_with_end[i+1]
        
        # Define the start and end pages for text extraction
        start_page = current_heading['page'] - 1
        end_page = next_heading['page'] - 1

        content = ""
        for page_num in range(start_page, end_page + 1):
            page = doc.load_page(page_num)
            
            # If start and end are on the same page, extract text between headings
            if start_page == end_page:
                # Find bounding boxes to define the extraction area
                start_rects = page.search_for(current_heading['text'])
                end_rects = page.search_for(next_heading['text'])
                if start_rects and end_rects:
                    clip_rect = fitz.Rect(0, start_rects[0].y1, page.rect.width, end_rects[0].y0)
                    content += page.get_text(clip=clip_rect)
            # If the section spans multiple pages
            else:
                if page_num == start_page: # From heading to bottom of page
                    start_rects = page.search_for(current_heading['text'])
                    if start_rects:
                        clip_rect = fitz.Rect(0, start_rects[0].y1, page.rect.width, page.rect.height)
                        content += page.get_text(clip=clip_rect)
                elif page_num == end_page: # From top of page to next heading
                    end_rects = page.search_for(next_heading['text'])
                    if end_rects:
                        clip_rect = fitz.Rect(0, 0, page.rect.width, end_rects[0].y0)
                        content += page.get_text(clip=clip_rect)
                else: # Full page content
                    content += page.get_text()
        
        section_data = current_heading.copy()
        section_data['content'] = content.strip().replace('\n', ' ')
        sections_with_content.append(section_data)
        
    return sections_with_content

# --- Main Execution Logic ---
def run_analysis():
    # Define directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. LOAD CONFIGURATION AND MODEL
    print("🧠 Loading configuration and AI model...")
    try:
        with open(input_dir / "config.json", 'r') as f:
            config = json.load(f)
        persona = config['persona']
        job = config['job_to_be_done']
    except FileNotFoundError:
        print("❌ Error: config.json not found in /app/input. Exiting.")
        return

    # Load the sentence embedding model. It's cached in the Docker image.
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    print("✅ Model loaded successfully.")

    # 2. PROCESS ALL PDFs and BUILD A SEARCHABLE CORPUS
    print("📚 Processing PDF documents...")
    all_sections = []
    pdf_files = list(input_dir.glob("*.pdf"))
    
    for pdf_path in pdf_files:
        print(f"  - Processing {pdf_path.name}")
        try:
            doc = fitz.open(pdf_path)
            # Use your 1A processor to get the document structure
            processor = AdvancedPDFProcessor(pdf_path)
            outline = processor.get_outline()['outline']
            print(f"  - INFO: Found {len(outline)} headings in {pdf_path.name}")
            # Use our helper function to get the text content for each section
            sections_with_content = extract_text_for_sections(doc, outline)
            
            for section in sections_with_content:
                section['document'] = pdf_path.name
                all_sections.append(section)
        except Exception as e:
            print(f"⚠️ Could not process {pdf_path.name}: {e}")

    if not all_sections:
        print("❌ No sections extracted from any PDF. Cannot perform analysis.")
        return
    print(f"✅ Found {len(all_sections)} sections across {len(pdf_files)} documents.")

    # 3. PERFORM SEMANTIC SEARCH AND RANKING
    print("🔍 Performing semantic search...")
    query = f"Persona: {persona}. Task: {job}"
    
    corpus_texts = [section.get('content', '') for section in all_sections]
    
    # Generate embeddings for the query and all section contents
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
    
    # Calculate cosine similarity to find the most relevant sections
    cosine_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    print("✅ Search complete.")

    # 4. ASSEMBLE THE FINAL JSON OUTPUT
    print("📝 Assembling final output...")
    output_data = {
        "metadata": {
            "input_documents": [p.name for p in pdf_files],
            "persona": persona['role'],
            "job_to_be_done": job['task'],
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": [],
        "sub_section_analysis": []
    }

    # Get the top 10 results
    top_results = torch.topk(cosine_scores, k=min(10, len(all_sections)))

    for rank, (score, idx) in enumerate(zip(top_results.values, top_results.indices)):
        section = all_sections[idx]
        
        # Add to the ranked list of sections
        output_data["extracted_sections"].append({
            "document": section['document'],
            "page_number": section['page'],
            "section_title": section['text'],
            "importance_rank": rank + 1,
            
        })
        
        # --- Generate "Refined Text" (Extractive Summary) ---
        # Split the section content into sentences
        sentences = re.split(r'(?<=[.!?])\s+', section['content'])
        if sentences:
            sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
            sent_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
            
            # Get the top 3 most relevant sentences
            top_sent_indices = torch.topk(sent_scores, k=min(3, len(sentences))).indices
            top_sent_indices = sorted(top_sent_indices.tolist()) # Sort to maintain order
            refined_text = " ".join([sentences[i] for i in top_sent_indices])
        else:
            refined_text = "No content available for summarization."

        output_data["sub_section_analysis"].append({
            "document": section['document'],
            "page_number": section['page'],
           
            "refined_text": refined_text
        })
    
    # Write the final JSON file
    output_path = output_dir / "challenge1b_output.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"🎉 Success! Output written to {output_path}")

if __name__ == "__main__":
    run_analysis()