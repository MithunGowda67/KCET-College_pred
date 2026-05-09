import pandas as pd
import os
import re
from difflib import get_close_matches

# Predefined valid branches
VALID_BRANCHES = [
    "Computer Science and Engineering",
    "Computer Science and Engineering (Data Science)",
    "Computer Science and Engineering (AI & ML)",
    "Information Science and Engineering",
    "Electronics and Communication Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electrical and Electronics Engineering",
    "Artificial Intelligence and Machine Learning",
    "Artificial Intelligence and Data Science",
    "Biotechnology",
    "Aerospace Engineering",
    "Aeronautical Engineering",
    "Automobile Engineering",
    "Chemical Engineering",
    "Mechatronics Engineering",
    "Robotics and Artificial Intelligence",
    "Cyber Security",
    "Computer Engineering",
    "Information Technology"
]

CITY_MAPPING = {
    "BANGALORE": "Bangalore",
    "BENGALURU": "Bangalore",
    "MYSORE": "Mysore",
    "MYSURU": "Mysore",
    "BELGAUM": "Belagavi",
    "BELAGAVI": "Belagavi",
    "TUMKUR": "Tumakuru",
    "TUMAKURU": "Tumakuru",
    "MANGALORE": "Mangaluru",
    "MANGALURU": "Mangaluru",
    "HUBLI": "Hubballi",
    "HUBBALLI": "Hubballi",
    "DHARWAD": "Dharwad",
    "GULBARGA": "Kalaburagi",
    "KALABURAGI": "Kalaburagi",
    "BELLARY": "Ballari",
    "BALLARI": "Ballari",
    "SHIMOGA": "Shivamogga",
    "SHIVAMOGGA": "Shivamogga",
    "BIJAPUR": "Vijayapura",
    "VIJAYAPURA": "Vijayapura",
    "DAVANGERE": "Davanagere",
    "HASSAN": "Hassan",
    "MANDYA": "Mandya",
    "UDUPI": "Udupi",
    "BIDAR": "Bidar",
    "KOPPAL": "Koppal",
    "RAICHUR": "Raichur",
    "CHITRADURGA": "Chitradurga",
    "KOLAR": "Kolar",
    "CHIKMAGALUR": "Chikkamagaluru",
    "CHIKKAMAGALURU": "Chikkamagaluru",
    "BAGALKOT": "Bagalkote",
    "BAGALKOTE": "Bagalkote"
}

def clean_city(name):
    if not isinstance(name, str): return "Unknown"
    
    # Extract the last part after comma
    parts = name.split(',')
    city_raw = parts[-1].strip().upper()
    
    # Remove pin codes (6 digits) and special chars
    city_raw = re.sub(r'\b\d{6}\b', '', city_raw)
    city_raw = re.sub(r'-\s*\d+', '', city_raw)
    city_raw = re.sub(r'[^A-Z\s]', '', city_raw)
    city_raw = city_raw.strip()
    
    # Try mapping
    for key, val in CITY_MAPPING.items():
        if key in city_raw:
            return val
            
    # Title case what remains
    if city_raw:
        return city_raw.title()
    return "Unknown"

def clean_branch(branch_raw):
    if not isinstance(branch_raw, str): return None
    
    # Clean up broken text
    b = branch_raw.upper().replace('\n', ' ')
    b = re.sub(r'\s+', ' ', b).strip()
    
    # Common replacements to help fuzzy matcher
    b = b.replace('ENGG', 'ENGINEERING')
    b = b.replace('COMMUNICATION', 'COMMUNICATION')
    b = b.replace('COMPUTER SCIENCE', 'COMPUTER SCIENCE')
    b = b.replace(' AND ', ' & ') # Temp for matching
    
    # Find closest match
    matches = get_close_matches(b, [v.upper().replace(' AND ', ' & ') for v in VALID_BRANCHES], n=1, cutoff=0.5)
    if matches:
        # map back to proper case
        idx = [v.upper().replace(' AND ', ' & ') for v in VALID_BRANCHES].index(matches[0])
        return VALID_BRANCHES[idx]
        
    return None

def determine_type(name):
    if not isinstance(name, str): return "Private"
    name_lower = name.lower()
    if 'govt' in name_lower or 'government' in name_lower or 'university' in name_lower:
        return "Government"
    elif 'autonomous' in name_lower:
        return "Autonomous"
    return "Private"

def clean_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    r1_path = os.path.join(data_dir, 'first_round.csv')
    r3_path = os.path.join(data_dir, 'third_round.csv')
    seats_path = os.path.join(data_dir, 'seat_matrix.csv')
    master_path = os.path.join(data_dir, 'master_dataset.csv')
    
    # Helper to clean individual df
    def process_df(df_path, col_name):
        if not os.path.exists(df_path):
            return pd.DataFrame()
            
        df = pd.read_csv(df_path)
        if df.empty: return df
        
        df['branch_clean'] = df['branch'].apply(clean_branch)
        df = df.dropna(subset=['branch_clean', 'cutoff'])
        
        # Aggregate duplicates (in case of fragmented parsing resulting in same branch)
        # Take the minimum cutoff for the same branch/college
        df['cutoff'] = pd.to_numeric(df['cutoff'], errors='coerce')
        df = df.dropna(subset=['cutoff'])
        
        df = df.groupby(['college_name', 'branch_clean', 'category'])['cutoff'].min().reset_index()
        df = df.rename(columns={'cutoff': col_name})
        return df

    df_r1 = process_df(r1_path, 'round1_cutoff')
    df_r3 = process_df(r3_path, 'round3_cutoff')
    
    if df_r1.empty and df_r3.empty:
        print("No Round 1 or Round 3 data found.")
        return
        
    # Merge rounds
    if not df_r1.empty and not df_r3.empty:
        merged_df = pd.merge(df_r1, df_r3, on=['college_name', 'branch_clean', 'category'], how='outer')
    elif not df_r1.empty:
        merged_df = df_r1.copy()
        merged_df['round3_cutoff'] = None
    else:
        merged_df = df_r3.copy()
        merged_df['round1_cutoff'] = None
        
    merged_df = merged_df.rename(columns={'branch_clean': 'branch'})
        
    # Apply city and type
    merged_df['city'] = merged_df['college_name'].apply(clean_city)
    merged_df['college_type'] = merged_df['college_name'].apply(determine_type)
    
    # Seats
    if os.path.exists(seats_path):
        df_seats = pd.read_csv(seats_path)
        if not df_seats.empty:
            df_seats['branch_clean'] = df_seats['branch'].apply(clean_branch)
            df_seats = df_seats.dropna(subset=['branch_clean'])
            df_seats['intake'] = pd.to_numeric(df_seats['intake'], errors='coerce')
            df_seats = df_seats.groupby(['college_name', 'branch_clean'])['intake'].sum().reset_index()
            df_seats = df_seats.rename(columns={'branch_clean': 'branch'})
            
            # Simple match by college string content
            def get_seat_intake(row):
                # Try to find a college in seats that is somewhat similar
                col_name_lower = row['college_name'].lower().split(',')[0]
                matches = df_seats[
                    (df_seats['college_name'].str.lower().str.contains(col_name_lower[:15], na=False)) & 
                    (df_seats['branch'] == row['branch'])
                ]
                if not matches.empty:
                    return matches['intake'].values[0]
                return None
                
            merged_df['intake'] = merged_df.apply(get_seat_intake, axis=1)
        else:
            merged_df['intake'] = None
    else:
        merged_df['intake'] = None
        
    # Final cleanup
    merged_df = merged_df.dropna(subset=['college_name'])
    
    merged_df.to_csv(master_path, index=False)
    print(f"Master dataset created at {master_path} with {len(merged_df)} records.")

if __name__ == "__main__":
    clean_dataset()
