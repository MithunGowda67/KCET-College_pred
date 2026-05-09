import pdfplumber
import sys

def extract_text(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i in range(min(5, len(pdf.pages))):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text += f"--- Page {i+1} ---\n" + page_text + "\n"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Extracted pages to {output_path}")

if __name__ == '__main__':
    extract_text(sys.argv[1], sys.argv[2])
