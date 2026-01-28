import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from modules.pdf_converter import PDFConverter

converter = PDFConverter(output_dir=".")
converter.markdown_to_pdf("test_ebook.md", output_pdf="test_ebook.pdf")
print("Test PDF conversion finished.")
