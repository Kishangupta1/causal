import pandas as pd
from binary_conversion import get_binary_key

if __name__ == "__main__":
    file_path = r"C:\Users\ADMIN\Desktop\work\Train\Causal_LLM\impact\binary_data\op\Modern_day_slavery_binary_mapped_variable_0.8.xlsx"
    df = pd.read_excel(file_path)
    binary_map = {"Gender": {0: ["male"], 1: ["female"]}, "Marital status": {0: ["single"], 1: ["married"]},
                  "Skilled / unskilled?": {0: ["unskilled"], 1: ["skilled"]}}
    worker_start_col = 3
    df = df.drop(columns=['unique_values'])
    df = df.drop(index=0).reset_index(drop=True)  # drop country of origin
    for idx, row in df.iterrows():
        if row['question'] in binary_map:
            df.iloc[idx, worker_start_col:] = df.iloc[idx, worker_start_col:].apply(
                lambda x: get_binary_key(x, binary_map[row['question'].strip()]))
    df.to_excel('op/Modern_day_slavery_binary_mapped_variable_final.xlsx', index=False, engine='xlsxwriter')
