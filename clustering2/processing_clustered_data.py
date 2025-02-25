import pandas as pd


df = pd.read_csv("modern_slavery_1st.csv")

# Remove columns that contain only NaN or -1
df_cleaned = df.drop(columns=[col for col in df.columns[4:] if df[col].apply(lambda x: pd.isna(x) or x == -1).all()])


print(df_cleaned)


