import json
import re
import pandas as pd
from tqdm import tqdm
import config as cfg
import ast


def clean_and_count(item):
    count = 0
    if isinstance(item, str):  # Check if it's a string (with surrounding text)
        # Use regex to extract the dictionary portion
        dict_str = re.search(r'\{.*?\}', item, re.DOTALL)
        try:
            if dict_str:
                item = ast.literal_eval(dict_str.group(0))  # Convert the extracted string to a dictionary
        except Exception as e:
            print("can't parse")

    if isinstance(item, dict):  # Proceed only if it's a valid dictionary
        for key, values in item.items():
            count += len(values)
    return count


if __name__ == '__main__':
    filepath = "op/ques_map_merged_socio_economic_ques.xlsx"
    df = pd.read_excel(filepath)
    col = df["cluster"]
    result = col.apply(clean_and_count)
    print('here')
