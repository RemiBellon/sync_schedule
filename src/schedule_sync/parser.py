import pandas as pd
from datetime import datetime

def parse_schedule(file_path: str):
    """
    Read the .ods schedule file and extract event as list
    """
    print(f"Lecture du fichier : {file_path}")

    # data column name are on line 2
    df = pd.read_excel(file_path, engine="odf", header=1)

    events = []

    for index, row in df.iterrows():
        date_str = str(row['Date']).strip()

        # Ignore empty lines
        if pd.isna(row['Date']) or date_str == 'nan':
            continue

        # --- Morning ---
        if pd.notna(row['Course']) and str(row['Course']).strip() != 'nan':
            events.append({
                'date': date_str,
                'time': str(row['Time']).strip(),
                'course': str(row['Course']).strip(),
                'location': str(row['Where']).strip() if pd.notna(row['Where']) else "",
                'professor': str(row['Who']).strip() if pd.notna(row['Who']) else ""
            })

        # --- Afeternoon ---
        # In pandas, the 2nd column with the same name get the suffixe '.1'
        if pd.notna(row['Course.1']) and str(row['Course.1']).strip() != 'nan':
            events.append({
                'date': date_str,
                'time': str(row['Time.1']).strip(),
                'course': str(row['Course.1']).strip(),
                'location': str(row['Where.1']).strip() if pd.notna(row['Where.1']) else "",
                'professor': str(row['Who.1']).strip() if pd.notna(row['Who.1']) else ""
            })

    print(f"Extraction over : {len(events)}")
    return events

if __name__ == "__main__":
    cours_extraits = parse_schedule("data/current_schedule.ods")
    for cours in cours_extraits[:5]:
        print(cours)