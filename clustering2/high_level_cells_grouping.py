import pandas as pd
import openpyxl
import json
import config as cfg
# from clustering import system_prompt
from tqdm import tqdm
import re
import requests
import ast
import numpy as np


tqdm.pandas()
# open prompt files
with open(cfg.high_level_group) as f:
    msg_high_level_group = json.load(f)


def system_prompt(question, rows_list, msg_data):
    # System msg
    msg_list = [json.dumps({"role": "system", "content": msg_data["system"]})]
    aug_msg_hypo = msg_data['history'][0][
                  'user'] + f"Question: {question} || Answers: {rows_list}"
    msg_list.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
    config = {
  "mirostat_tau": 1,
  "num_ctx": 15000,
  "num_predict": -1,
  "repeat_last_n": 64,
  "repeat_penalty": 1.1,
  "stop": [
    ""
  ],
  "temperature": 0,
  "top_k": 1,
  "top_p": 0.9
}
    try:
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list,
                                                                       'configuration': json.dumps(config)})
        str_out = res_hypo.content.decode()
        result = json.loads(str_out.strip())['content']
    except Exception as e:
        result = ""
        print(f"can't do with error {e}")
    return result


def only_nums(unique_val):
    # Pattern to check only numerical vals
    # pattern = r"^\[\s*(?:nan|NaN|\'\s*\'|\d+\.?\d*)(?:\s*,\s*(?:nan|NaN|\'\s*\'|\d+\.?\d*))*\s*\]$"
    # return bool(re.match(pattern, s))
    for num in unique_val:
        if isinstance(num, str):
            return False
    return True


def apply_map(value, mapping_dict):
    for key, info in mapping_dict.items():
        if value in info['value']:
            return info['mapping']
    return int(-1)


def process_row(row, df, start_col, system_prompt, only_nums, apply_map, msg_high_level_group):
    # Extract the worker data starting from 'start_col'
    df_workers = row.iloc[start_col:]

    # Get unique values from the row, dropping NaN values
    unique_values = list(pd.unique(df_workers.dropna()))
    unique_value_list.append(unique_values)
    # If all unique values are numeric, return early
    if only_nums(unique_values):
        cluster.append("")
        return

    # Generate system output based on the question and unique values
    op = system_prompt(row['question'], unique_values, msg_high_level_group)

    try:
        op_json = json.loads(op)
    except Exception as e:
        print(f"can't parse {row.name} and{row['question']}")
        cluster.append("Error")
        return
    # Parse the output and build the mapping dictionary
    temp_dict = {
        key: {"value": val, "mapping": idx}
        for idx, (key, val) in enumerate(op_json.items())
    }
    cluster.append(temp_dict)

    # Function to map a column value and return the new value or -1 if NaN
    def map_column_value(col_value):
        if pd.notna(col_value):
            return apply_map(col_value, temp_dict)
        else:
            return int(-1)

    # Modify the DataFrame in-place by applying `map_column_value` to relevant columns
    df.iloc[row.name, start_col:] = df.iloc[row.name, start_col:].apply(map_column_value)


if __name__ == "__main__":
    filepath = r"C:\Users\Kishan Gupta\Desktop\TrainModules\Causal_LLM\impact\clustering2\ques_map_merged_socio_economic_ques1.xlsx"
    # filepath = r"test_no.xlsx"
    # Load the Excel file using pandas and openpyxl
    df = pd.read_excel(filepath)
    start_col = 3
    cluster = []
    unique_value_list = []
    df.progress_apply(lambda row: process_row(row, df, start_col, system_prompt, only_nums, apply_map, msg_high_level_group),
             axis=1)
    df.insert(0, 'clusters', cluster)
    df.insert(1, 'unique_value', unique_value_list)
    df.to_csv(f"test_result1.csv")
    print("Done")
