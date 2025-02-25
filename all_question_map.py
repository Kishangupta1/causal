import json
import pandas as pd
from tqdm import tqdm


json1 = "map_expand.json"
json2 = "merge_similar_map.json"
json3 = "merge_iter_map.json"
filepath = "op/31.07.24 Impactt Dataset.xlsx"
map_file = "op/map_ques.xlsx"
with open(json1) as f:
    data1 = json.load(f)
with open(json2) as f:
    data2 = json.load(f)
with open(json3) as f:
    data3 = json.load(f)

df = pd.read_excel(filepath)
map_df = pd.read_excel(map_file)
map_dict = dict(zip(map_df['mapping'], map_df['question']))


def get_key_for_value_in_list(d, search_value):
    for key, value_list in d.items():
        if len(value_list) > 1:
            if any(search_value.lower().strip() == value.lower().strip() for value in value_list):
                return key
        else:
            if search_value in value_list:
                return key
    return search_value


column_dict = {"Questions": [], "Mapping": []}
for idx in tqdm(range(len(df)), desc="Processing"):
    print(f"Processing idx: {idx}")
    key1 = get_key_for_value_in_list(data2, data1[str(idx)])
    key2 = get_key_for_value_in_list(data3, key1)
    map_val = get_key_for_value_in_list(map_dict, key2)
    column_dict["Questions"].append(df['Questions'][idx])
    column_dict["Mapping"].append(map_val)

 # new df
df3 = pd.DataFrame()
for col_name, col_values in column_dict.items():
    df3[col_name] = col_values

# Save the updated DataFrame back to an Excel file
output_path = 'op/Final_question_map.xlsx'  # Replace with desired output file path
df3.to_excel(output_path, index=False)
