import fitz  # PyMuPDF
import statistics
import re
from collections import defaultdict
import os

class AdvancedPDFProcessor:
    """
    Extracts a document outline using a sophisticated feature-based scoring model.
    """
    def __init__(self, pdf_path):
        """Initializes the extractor with a path to a PDF file."""
        self.doc = fitz.open(pdf_path)
        self.min_score_threshold = 7
        
        self.lines = self._extract_lines_with_features()
        self.body_style = self._find_dominant_style()
        self._score_lines()
        self.heading_level_map = self._classify_heading_styles()

    # --- MODIFICATION START: Only the footer area is now ignored ---
    def _extract_lines_with_features(self):
        """Extracts every line of text and enriches it with a feature set."""
        lines = []
        for page_num, page in enumerate(self.doc):
            page_height = page.rect.height
            # Define only a bottom margin to ignore the footer area (bottom 10%)
            bottom_margin = page_height * 0.90

            prev_y = 0
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:  # Text block
                    for line in block['lines']:
                        line_text = "".join(s['text'] for s in line['spans']).strip()
                        if not line_text:
                            continue

                        x0, y0, x1, y1 = line['bbox']
                        
                        # Ignore text only if it's in the footer area
                        if y0 > bottom_margin:
                            continue
                        
                        first_span = line['spans'][0]
                        font_size = round(first_span['size'])
                        is_bold = "bold" in first_span['font'].lower()
                        
                        features = {
                            "text": line_text,
                            "page": page_num + 1,
                            "font_size": font_size,
                            "is_bold": is_bold,
                            "score": 0, # Will be calculated later
                            "style_key": (font_size, is_bold)
                        }
                        lines.append(features)
                        prev_y = y1
        return lines
    # --- MODIFICATION END ---

    def _find_dominant_style(self):
        """Finds the most common style (size, bold) to identify body text."""
        if not self.lines:
            return (10, False)
        style_counts = defaultdict(int)
        for line in self.lines:
            style_counts[line['style_key']] += len(line['text'])
        return max(style_counts, key=style_counts.get)

    def _score_lines(self):
        """
        Calculates a 'heading_score' for each line. A line is only a potential
        heading if it is followed by a line with a smaller font size.
        """
        body_size = self.body_style[0]

        for i, line in enumerate(self.lines):
            score = 0
            if i + 1 < len(self.lines):
                next_line = self.lines[i+1]
                
                if line['font_size'] > next_line['font_size']:
                    if line['font_size'] > body_size:
                        score += (line['font_size'] - body_size) * 1.5
                    if line['is_bold'] and not self.body_style[1]: 
                        score += 5
                    if len(line['text'].split()) < 10: 
                        score += 2
            
            line['score'] = score

    def _classify_heading_styles(self):
        """
        Groups all high-scoring styles and maps them to H1, H2, and H3.
        """
        potential_styles = sorted(
            list({line['style_key'] for line in self.lines if line['score'] > self.min_score_threshold}),
            key=lambda x: x[0], # Sort by font size
            reverse=True
        )

        level_map = {}
        if len(potential_styles) > 0:
            level_map[potential_styles[0]] = "H1"
        if len(potential_styles) > 1:
            level_map[potential_styles[1]] = "H2"
        if len(potential_styles) > 2:
            for style in potential_styles[2:]:
                level_map[style] = "H3"

        return level_map

    # --- MODIFICATION START: Title is now all text with the largest font size on page 1 ---
    def get_outline(self):
        """Constructs the final JSON output."""
        outline = []
        
        title = "Untitled Document"
        page1_lines = [l for l in self.lines if l['page'] == 1]
        
        if page1_lines:
            # Find the largest font size that appears on the first page
            max_font_size = max(l['font_size'] for l in page1_lines)
            
            # Check if this font size is larger than the body text
            if max_font_size > self.body_style[0]:
                # Collect text from all lines that have this maximum font size
                title_parts = [l['text'] for l in page1_lines if l['font_size'] == max_font_size]
                title = " ".join(title_parts)

        # Build the outline
        for line in self.lines:
            style = line['style_key']
            if style in self.heading_level_map:
                # Avoid adding parts of the title to the outline
                if line['text'] in title and line['page'] == 1 and line['font_size'] == max_font_size:
                    continue
                
                outline.append({
                    "level": self.heading_level_map[style],
                    "text": line['text'],
                    "page": line['page']
                })

        return {"title": title, "outline": outline}
    # --- MODIFICATION END ---