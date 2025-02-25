import pandas as pd

# Sample DataFrame
data = {
    'A': [1, None, 3, 4, None, 6],
    'B': [None, 2, 3, None, 5, None],
    'C': [1, 2, None, None, 5, 6],
    'D': [None, None, 3, 4, None, None]
}

df = pd.DataFrame(data)

# Step 1: Identify filled columns per row
filled_mask = df.notna()

# Step 2: Group rows based on common filled columns
column_groups = {}
for col in df.columns:
    matching_rows = filled_mask.index[filled_mask[col]].tolist()
    if len(matching_rows) > 1:  # Only consider groups with at least 2 rows
        column_groups.setdefault(tuple(matching_rows), []).append(col)

# Step 3: Extract and print separate DataFrames
dfs = [df.loc[list(rows), cols] for rows, cols in column_groups.items()]

# Print the grouped DataFrames
for i, d in enumerate(dfs):
    print(f"Group {i} (Rows {list(d.index)}, Columns {list(d.columns)}):\n{d}\n")
