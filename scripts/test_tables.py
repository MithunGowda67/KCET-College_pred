import pdfplumber
import sys
import json

def test_tables(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        tables = first_page.extract_tables()
        print(f"Found {len(tables)} tables")
        if tables:
            print(json.dumps(tables[0][:5], indent=2))

if __name__ == '__main__':
    test_tables(sys.argv[1])
