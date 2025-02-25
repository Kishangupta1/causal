import pandas as pd
import re
from tqdm import tqdm


filepath = r"op/31.07.24 Impactt Dataset.xlsx"
df = pd.read_excel(filepath, sheet_name="Socio Economic")
# filepath = r"op/test.xlsx"
# df = pd.read_excel(filepath)

# Initialize variables
data = {}
current_worker = None

# Iterate through the DataFrame rows
pattern = r'^\s*(contractor|contractor name)\s*$'  # split dataset based on contractor/contractor name
prev_row_val = None
for index, row in df.iterrows():
    if str(row.values[1]).lower().strip() != "nan" and re.match(pattern, row.values[1], re.IGNORECASE):
        current_worker = 'dataset' + '_' + str(index)  # Assuming the contractor name is in the second column
        data[current_worker] = []
        data[current_worker].append(row.values)
        prev_row_val = row.values[0]
    else:
        if isinstance(row.values[1], str):
            row.values[1] = re.sub(r'[^\x00-\x7F]+', ' ', row.values[1])  # remove non-english characters
        # if row.values[0] == prev_row_val:  # Add data only of similar date # not needed # modified the data
        data[current_worker].append(row.values)

# Create a new DataFrame from the collected data
result = pd.DataFrame()
for idx, (worker, answers) in tqdm(enumerate(data.items()), desc="Progress"):
    worker_answers = [answer[1:] for answer in answers[:]]  # Exclude the first column(year) which is the question identifier
    worker_df = pd.DataFrame(worker_answers)
    worker_df_cleaned = worker_df.dropna(axis=1, how='all')
    first_header = {0: 'question'}
    worker_df_cleaned.rename(columns=first_header, inplace=True)
    if idx != 0:
        # Split the new DataFrame
        rows_to_add = worker_df_cleaned[['question']]
        # add year to row
        rows_to_add.loc[len(rows_to_add)] = "year"
        columns_to_add = worker_df_cleaned.iloc[:, 1:]
        # Append the rows to the existing DataFrame
        df_combined_rows = pd.concat([result, rows_to_add], ignore_index=True)
        # Create a new DataFrame for columns to add
        # Ensuring we have the same index length as the combined rows DataFrame
        columns_to_add = columns_to_add.reset_index(drop=True)
        # Align the columns to the correct index positions
        columns_to_add = pd.concat([pd.DataFrame(index=result.index), columns_to_add], ignore_index=True)
        # Reset the column header
        column_headers = ['worker_' + str(i + len(result.columns)) for i in range(len(columns_to_add.columns))]
        columns_to_add.columns = column_headers
        # Add year row
        columns_to_add.loc[len(columns_to_add)] = [answers[0][0]] * len(columns_to_add.columns)
        # Combine the DataFrames
        result = pd.concat([df_combined_rows, columns_to_add], axis=1)
    else:
        start_index = 1
        # Reset the column header from 2nd col
        column_headers = ['worker_' + str(i) for i in range(start_index, len(worker_df_cleaned.columns))]
        worker_df_cleaned.columns = [worker_df_cleaned.columns[i] if i < start_index else column_headers[i-start_index] for i in
                      range(len(worker_df_cleaned.columns))]
        worker_df_cleaned.loc[len(worker_df_cleaned)] = ["year"] + [answers[0][0]] * (len(worker_df_cleaned.columns) - 1)  # set a row for year
        result = pd.concat([result, worker_df_cleaned], axis=1)

# write to csv file
# result_t = result.transpose()
result.to_excel('op/socio_economic.xlsx', index=False, engine='xlsxwriter')
# result.to_csv('socio_economic.csv', index=False, encoding="utf-8")
