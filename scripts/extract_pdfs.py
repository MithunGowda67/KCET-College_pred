import pdfplumber
import pandas as pd
import re
import os

def extract_cutoff_pdf(pdf_path, output_csv):
    print(f"Extracting cutoffs from {pdf_path}...")
    data = []
    
    # We will iterate through lines. Using pdfplumber extract_text is easier 
    # to maintain the order of college -> course cutoffs.
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            current_college = ""
            current_course = ""
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Match college name
                if line.startswith("College:"):
                    current_college = line.replace("College:", "").strip()
                    i += 1
                    continue
                    
                # Match Course Name header
                if line.startswith("Course Name"):
                    categories = line.split()[2:] # Skip 'Course', 'Name'
                    i += 1
                    
                    # The following lines will be course name and cutoffs
                    # Course names can span multiple lines.
                    course_name_parts = []
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if sub_line.startswith("College:") or sub_line.startswith("Course Name") or "Page" in sub_line or "Generated on" in sub_line or sub_line == "":
                            break
                            
                        # If the line contains at least one number, it might be the cutoff line
                        tokens = sub_line.split()
                        if any(re.match(r'^\d+(\.\d+)?$', t) or t == '--' for t in tokens[-5:]):
                            # This is a cutoff line. Find where cutoffs start
                            # A cutoff token is either a number or '--'
                            cutoff_start_idx = -1
                            for idx, t in enumerate(tokens):
                                if re.match(r'^\d+(\.\d+)?$', t) or t == '--' or "Lakh" in t:
                                    # Wait, sometimes '2AG' has numbers. Let's just find the first token that is a valid cutoff
                                    # We know categories length.
                                    pass
                            
                            # A more robust way:
                            # The last N tokens are cutoffs, matching the length of categories
                            num_cats = len(categories)
                            if len(tokens) >= num_cats:
                                course_name_parts.append(" ".join(tokens[:-num_cats]))
                                cutoffs = tokens[-num_cats:]
                                
                                course_name = " ".join(course_name_parts).strip()
                                
                                # Find GM cutoff (General Merit)
                                gm_cutoff = '--'
                                try:
                                    if 'GM' in categories:
                                        gm_idx = categories.index('GM')
                                        gm_cutoff = cutoffs[gm_idx]
                                except:
                                    pass
                                    
                                data.append({
                                    "college_name": current_college,
                                    "branch": course_name,
                                    "category": "GM",
                                    "cutoff": gm_cutoff
                                })
                                course_name_parts = []
                            else:
                                course_name_parts.append(sub_line)
                        else:
                            course_name_parts.append(sub_line)
                        i += 1
                    continue
                i += 1
                
    df = pd.DataFrame(data)
    # clean up the cutoffs
    df['cutoff'] = df['cutoff'].replace('--', None)
    df['cutoff'] = pd.to_numeric(df['cutoff'], errors='coerce')
    df = df.dropna(subset=['cutoff'])
    
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} records to {output_csv}")

def extract_seat_matrix(pdf_path, output_csv):
    print(f"Extracting seat matrix from {pdf_path}...")
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            current_college = ""
            for line in lines:
                line = line.strip()
                if line.startswith("Address :"):
                    # College name is usually the line before
                    continue
                
                # Check if it's a course line. Starts with a number, then course name, then numbers
                match = re.match(r'^\d+\s+([A-Za-z\s&()]+?)\s+(\d+)\s+(\d+)', line)
                if match:
                    branch = match.group(1).strip()
                    total_intake = match.group(2)
                    # We need a proper college name, let's just use a dummy or try to find it.
                    # This is just a quick extraction.
                    data.append({
                        "college_name": current_college,
                        "branch": branch,
                        "intake": total_intake
                    })
                elif not line.startswith("Sl.N") and not line.startswith("o.") and not line.startswith("Seats") and not line.startswith("Intake") and not line.startswith("5%") and not line.startswith("SEATS") and not line.startswith("Ins Total") and not "Page" in line and not "ANNEXURE" in line and not "Address" in line:
                    if len(line) > 10 and not any(char.isdigit() for char in line):
                         current_college = line.strip()

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} records to {output_csv}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    extract_cutoff_pdf("../first round.pdf", os.path.join(data_dir, "first_round.csv"))
    extract_cutoff_pdf("../3rd round cut off.pdf", os.path.join(data_dir, "third_round.csv"))
    extract_seat_matrix("../Seat_Matrix_05072025english.pdf", os.path.join(data_dir, "seat_matrix.csv"))
