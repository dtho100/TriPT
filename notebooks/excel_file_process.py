import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import datetime

def process_excel_files(input_files, parent_path=None):
    processed_data = pd.DataFrame()
    for file in input_files:
        if parent_path == None:
            df = pd.read_excel(Path.cwd() / file)
        else:
            df = pd.read_excel(parent_path + '/' + file)
        df_filtered = df[~df['Date'].isna()]
        
        processed_data = pd.concat([processed_data, df_filtered], ignore_index = True)
    processed_data['Date'] = pd.to_datetime(processed_data['Date'])
    processed_data['Week'] = processed_data['Week'].round().astype(int)

    for session in range(1,3):
        details_col = f"Session {session} Details"
        modality_col = f"Session {session} Modality"

        swim_mask = (processed_data[modality_col] == 'Swim') & (processed_data[details_col].str.contains(' m ', case=False, na=False))
        processed_data.loc[swim_mask, details_col] = processed_data.loc[swim_mask, details_col].str.replace(' m ', ' meter ', regex=False)

        min_mask = (processed_data[details_col].str.contains('′', case=False, na=False))
        processed_data.loc[min_mask, details_col] = processed_data.loc[min_mask, details_col].str.replace('′', ' min', regex=False)

        thousands_mask = (processed_data[details_col].str.contains(r'(?<=\d) (?=\d{3})', regex=True, na=False))
        processed_data.loc[thousands_mask, details_col] = processed_data.loc[thousands_mask, details_col].str.replace(r'(?<=\d) (?=\d{3})', '', regex=True)

    processed_data.sort_values(by='Date', inplace=True)
    processed_data.reset_index(drop=True, inplace=True)
    return processed_data


#df = process_excel_files(['build_weeks_17_20.xlsx', 'base_weeks_13_16.xlsx'], '/Users/daleythomsen/Downloads')

# for session in range(1,3):
#     details_col = f"Session {session} Details"
#     modality_col = f"Session {session} Modality"

#     swim_mask = (df[modality_col] == 'Swim') & (df[details_col].str.contains(' m ', case=False, na=False))
#     df.loc[swim_mask, details_col] = df.loc[swim_mask, details_col].str.replace(' m ', ' meter ', regex=False)

#     min_mask = (df[details_col].str.contains('′', case=False, na=False))
#     df.loc[min_mask, details_col] = df.loc[min_mask, details_col].str.replace('′', ' min', regex=False)

#     thousands_mask = (df[details_col].str.contains(r'(?<=\d) (?=\d{3})', regex=True, na=False))
#     df.loc[thousands_mask, details_col] = df.loc[thousands_mask, details_col].str.replace(r'(?<=\d) (?=\d{3})', '', regex=True)

def write_to_csv(processed_data, parent_path=None, output_file_name = 'combined'):
    current_time = str(datetime.datetime.now().strftime("%Y%m%d"))
    if parent_path == None:
        output_path = f"{Path.cwd()}/{str(output_file_name)}_{current_time}.csv"
    else:
        output_path = f"{parent_path}/{str(output_file_name)}_{current_time}.csv"
    processed_data.to_csv(output_path)
    print(f"File written to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Combine training CSV files.")
    parser.add_argument("parent_path")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("-o", "--output", default="combined")
    args = parser.parse_args()

    df = process_excel_files(input_files=args.inputs, parent_path=args.parent_path)
    #print(df['Session 1 Details'].head())
    write_to_csv(processed_data=df, parent_path=args.parent_path, output_file_name=args.output)
