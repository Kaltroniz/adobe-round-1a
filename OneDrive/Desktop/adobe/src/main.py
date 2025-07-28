import json
from pathlib import Path
from advanced_processor import AdvancedPDFProcessor

def main():
    """
    Main execution script.
    - Scans the /app/input directory for PDF files.
    - Processes each PDF using the AdvancedPDFProcessor.
    - Writes the output as a JSON file to the /app/output directory.
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in /app/input.")
        return

    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")
        try:
            # Instantiate the advanced processor and get the outline
            processor = AdvancedPDFProcessor(pdf_path)
            outline_data = processor.get_outline()
            
            # Define the output path
            output_filename = pdf_path.stem + ".json"
            output_path = output_dir / output_filename
            
            # Write the JSON data to the output file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(outline_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully generated {output_path.name}")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {e}")
            # Optionally, write an error JSON
            error_output_path = output_dir / (pdf_path.stem + ".error.json")
            with open(error_output_path, 'w') as f:
                json.dump({"error": str(e), "file": pdf_path.name}, f, indent=2)


if __name__ == "__main__":
    main()