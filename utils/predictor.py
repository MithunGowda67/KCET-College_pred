import pandas as pd

def classify_chance(rank, cutoff):
    if pd.isna(cutoff):
        return "Unknown"
        
    rank = float(rank)
    cutoff = float(cutoff)
    
    if rank < cutoff - 2000:
        return "Safe"
    elif cutoff - 2000 <= rank <= cutoff + 2000:
        return "Moderate"
    elif rank > cutoff + 2000:
        return "Dream"
    return "Unknown"

def calculate_chance_pct(rank, cutoff):
    if pd.isna(cutoff):
        return 0
    # Simple heuristic
    diff = cutoff - rank
    if diff > 5000: return 99
    if diff > 2000: return 85
    if diff > 0: return 60
    if diff > -2000: return 30
    if diff > -5000: return 10
    return 1

def predict_colleges(df, rank, category='GM', cities=None, branches=None, college_type=None, round_filter='Both'):
    """
    Predict colleges based on user rank and filters using dynamic margins.
    """
    if df.empty:
        return pd.DataFrame()
        
    result_df = df.copy()
    
    # Dynamic margin based on rank
    if rank < 5000:
        margin = 1500
    elif rank < 20000:
        margin = 3000
    else:
        margin = 7000
        
    lower_bound = rank - margin
    upper_bound = rank + margin
    
    # Filter by category if possible
    if 'category' in result_df.columns:
        cat_df = result_df[result_df['category'] == category]
        if not cat_df.empty:
            result_df = cat_df

    # We check cutoffs based on the selected round
    if round_filter == 'First Round' and 'round1_cutoff' in result_df.columns:
        mask = (result_df['round1_cutoff'] >= lower_bound) & (result_df['round1_cutoff'] <= upper_bound)
        result_df = result_df[mask].copy()
        result_df['chance'] = result_df['round1_cutoff'].apply(lambda c: classify_chance(rank, c))
        result_df['Difference'] = result_df['round1_cutoff'] - rank
        result_df['Chance %'] = result_df['round1_cutoff'].apply(lambda c: calculate_chance_pct(rank, c))
    elif round_filter == 'Third Round' and 'round3_cutoff' in result_df.columns:
        mask = (result_df['round3_cutoff'] >= lower_bound) & (result_df['round3_cutoff'] <= upper_bound)
        result_df = result_df[mask].copy()
        result_df['chance'] = result_df['round3_cutoff'].apply(lambda c: classify_chance(rank, c))
        result_df['Difference'] = result_df['round3_cutoff'] - rank
        result_df['Chance %'] = result_df['round3_cutoff'].apply(lambda c: calculate_chance_pct(rank, c))
    else:
        # Both rounds
        r1_valid = False
        r3_valid = False
        if 'round1_cutoff' in result_df.columns:
            r1_valid = (result_df['round1_cutoff'] >= lower_bound) & (result_df['round1_cutoff'] <= upper_bound)
        if 'round3_cutoff' in result_df.columns:
            r3_valid = (result_df['round3_cutoff'] >= lower_bound) & (result_df['round3_cutoff'] <= upper_bound)
            
        if 'round1_cutoff' in result_df.columns and 'round3_cutoff' in result_df.columns:
            mask = r1_valid | r3_valid
            result_df = result_df[mask].copy()
            # Prioritize R3 for chance if available
            result_df['chance'] = result_df.apply(
                lambda row: classify_chance(rank, row['round3_cutoff'] if pd.notna(row['round3_cutoff']) else row['round1_cutoff']),
                axis=1
            )
            result_df['Difference'] = result_df.apply(
                lambda row: (row['round3_cutoff'] if pd.notna(row['round3_cutoff']) else row['round1_cutoff']) - rank,
                axis=1
            )
            result_df['Chance %'] = result_df.apply(
                lambda row: calculate_chance_pct(rank, row['round3_cutoff'] if pd.notna(row['round3_cutoff']) else row['round1_cutoff']),
                axis=1
            )
        else:
            return pd.DataFrame()

    # Apply other filters (Now using multiselect lists)
    if cities and "All" not in cities:
        result_df = result_df[result_df['city'].isin(cities)]
        
    if branches and "All" not in branches:
        result_df = result_df[result_df['branch'].isin(branches)]
        
    if college_type and college_type != "All":
        result_df = result_df[result_df['college_type'] == college_type]
        
    # Calculate trend if both rounds available
    if 'round1_cutoff' in result_df.columns and 'round3_cutoff' in result_df.columns:
        result_df['trend'] = result_df['round3_cutoff'] - result_df['round1_cutoff']
        
    # Intelligent Sorting: Safe -> Higher cutoffs
    chance_map = {"Safe": 1, "Moderate": 2, "Dream": 3, "Unknown": 4}
    if not result_df.empty:
        result_df['chance_sort'] = result_df['chance'].map(chance_map)
        result_df = result_df.sort_values(['chance_sort', 'Difference'], ascending=[True, False]).drop('chance_sort', axis=1)
    
    return result_df
