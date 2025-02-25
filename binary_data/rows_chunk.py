import pandas as pd

file_path = r"C:\Users\ADMIN\Desktop\work\Train\Causal_LLM\impact\binary_data\op\Modern_day_slavery_binary_mapped_variable_final.xlsx"

df = pd.read_excel(file_path)
# df = df.drop(columns=['mapped_variable', 'context', 'unique_value'])
common_col_range = 1
common_cols = df.columns[:common_col_range]
# Step 1: Identify filled columns per row
filled_mask = df.notna()

# Step 2: Group rows based on common filled columns
column_groups = {}
for col in df.columns[common_col_range:]:
    matching_rows = filled_mask.index[filled_mask[col]].tolist()
    if len(matching_rows) > 1:  # Only consider groups with at least 2 rows
        column_groups.setdefault(tuple(matching_rows), []).append(col)

# Step 3: Extract and print separate DataFrames
dfs = [
    df.loc[list(rows), list(common_cols) + list(set(cols))]
    for rows, cols in column_groups.items()
]

# Sort based on the number of rows (descending) and then number of columns (ascending)
dfs.sort(key=lambda x: (-len(x), -len(x.columns)))


for i in range(len(dfs)):
    dfs[i] = dfs[i].dropna(axis=1, how='all')
    dfs[i].to_excel(f"op/chunks/modern_slavery_{len(dfs[i])}_{len(dfs[i].columns)}.xlsx", index=False, engine='xlsxwriter')