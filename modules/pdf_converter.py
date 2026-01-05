"""
Markdown to PDF Converter
Converts generated ebooks to professional PDF format
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import markdown
from bs4 import BeautifulSoup
from utils.logger import get_logger
from utils.helpers import load_niches, sanitize_filename

logger = get_logger("pdf_converter")

class PDFConverter:
    def __init__(self, output_dir="data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("PDFConverter initialized")
    
    def markdown_to_pdf(self, md_file, cover_image=None, output_pdf=None):
        """Convert markdown file to PDF"""
        logger.info(f"Converting {md_file} to PDF")
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Setup PDF
        if output_pdf is None:
            output_pdf = md_file.replace('.md', '.pdf')
        
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#34495e',
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Add cover image if provided
        if cover_image and os.path.exists(cover_image):
            try:
                img = RLImage(cover_image, width=4*inch, height=6*inch)
                story.append(Spacer(1, 1*inch))
                story.append(img)
                story.append(PageBreak())
            except Exception as e:
                logger.warning(f"Could not add cover image: {e}")
        
        # Process HTML content
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
            if element.name == 'h1':
                story.append(Paragraph(element.get_text(), title_style))
                story.append(Spacer(1, 0.2*inch))
            elif element.name in ['h2', 'h3']:
                story.append(Paragraph(element.get_text(), heading_style))
            elif element.name == 'p':
                text = element.get_text()
                if text.strip():
                    story.append(Paragraph(text, body_style))
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    bullet_text = f"• {li.get_text()}"
                    story.append(Paragraph(bullet_text, body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        try:
            doc.build(story)
            logger.success(f"Created PDF: {output_pdf}")
            return output_pdf
        except Exception as e:
            logger.error(f"Failed to create PDF: {e}")
            raise
    
    def convert_all(self, niches=None):
        """Convert all ebooks to PDF"""
        if niches is None:
            niches = load_niches()
        
        logger.info(f"Converting {len(niches)} ebooks to PDF...")
        
        converted_files = []
        for niche in niches.keys():
            md_file = self.output_dir / f"{sanitize_filename(niche)}_ebook.md"
            cover_file = self.output_dir / f"{sanitize_filename(niche)}_cover.png"
            pdf_file = self.output_dir / f"{sanitize_filename(niche)}_ebook.pdf"
            
            if md_file.exists():
                try:
                    self.markdown_to_pdf(
                        str(md_file),
                        str(cover_file) if cover_file.exists() else None,
                        str(pdf_file)
                    )
                    converted_files.append(str(pdf_file))
                except Exception as e:
                    logger.error(f"Failed to convert {niche}: {e}")
            else:
                logger.warning(f"Markdown file not found for {niche}")
        
        logger.success(f"Converted {len(converted_files)} PDFs")
        return converted_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert ebooks to PDF')
    parser.add_argument('--test-mode', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    converter = PDFConverter()
    converter.convert_all()

if __name__ == "__main__":
    main()
