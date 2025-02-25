import pandas as pd

# Example DataFrame
data = {
    "A": [1, 2, 2, 4],
    "B": [5, 2, 7, 6],
    "C": ["apple", "apple", "banana", "banana"],
}

df = pd.DataFrame(data)

# Get unique elements for each row
unique_per_row = df.apply(lambda row: row.unique(), axis=1)

# Convert the result into a DataFrame for easier inspection
unique_per_row_df = unique_per_row.to_frame(name="Unique Elements").reset_index()

print("Unique elements for each row:")
print(unique_per_row)
