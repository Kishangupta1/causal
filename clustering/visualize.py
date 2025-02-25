import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv('check_data.xlsx.csv')

# Function to classify each cell as text, number, or mixed
def classify_cell(value):
    if isinstance(value, str):
        # Check if it's text or mixed with numbers
        if any(char.isdigit() for char in value):
            return 'M'  # Mixed (text + numbers)
        else:
            return 'T'  # Text only
    elif isinstance(value, (int, float, np.number)):
        return 'N'  # Number only
    else:
        return 'U'  # Undefined

# Apply the classification function to each cell in the DataFrame
classified_df = df.applymap(classify_cell)

# Generate a heatmap based on classifications
# Assigning numeric values for heatmap (T=0, N=1, M=2, U=3)
heatmap_values = classified_df.replace({'T': 0, 'N': 1, 'M': 2, 'U': 3})

# Plotting the heatmap
plt.figure(figsize=(15, 10))
sns.heatmap(heatmap_values, annot=classified_df, cmap='coolwarm', cbar=False)
plt.title("Cell Classification (T=Text, N=Number, M=Mixed, U=Undefined)")
plt.show()
