import pandas as pd
import openpyxl
import json
import config as cfg
from clustering import system_prompt
from tqdm import tqdm
import re
import requests
import ast
import numpy as np

# open prompt files
with open(cfg.text_to_num) as f:
    msg_text_to_nums = json.load(f)

with open(cfg.categorical_val) as f:
    msg_categorical_val = json.load(f)

with open(cfg.others_cell) as f:
    msg_others_cell = json.load(f)

# def system_prompt(question, rows_list, msg_data):
#     # System msg
#     msg_list = [json.dumps({"role": "system", "content": msg_data["system"]})]
#     aug_msg_hypo = msg_data['history'][0][
#                   'user'] + f"Question: {question} || Answers: {rows_list}"
#     msg_list.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
#     config = {
#   "mirostat_tau": 1,
#   "num_ctx": 8000,
#   "num_predict": -1,
#   "repeat_last_n": 64,
#   "repeat_penalty": 1.1,
#   "stop": [
#     ""
#   ],
#   "temperature": 0,
#   "top_k": 1,
#   "top_p": 0.9
# }
#     try:
#         res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list,
#                                                                        'configuration': json.dumps(config)})
#         str_out = res_hypo.content.decode()
#         result = json.loads(str_out.strip())['content']
#     except Exception as e:
#         result = ""
#         print(f"can't do with error {e}")
#     return result


filepath = r"C:\Users\Kishan Gupta\Desktop\TrainModules\Causal_LLM\impact\op\ques_map_merged_socio_economic_ques.xlsx"
# Load the Excel file using pandas and openpyxl
df = pd.read_excel(filepath, engine='openpyxl')

# Load the Excel file using openpyxl to get the formatting
wb = openpyxl.load_workbook(filepath)
sheet = wb.active  # Automatically gets the first (and only) sheet

# Define a dictionary for common colors and their corresponding RGB values
color_mapping = {
    'C00000': 'red',
    'FFFF00': 'yellow',
    'FFC000': 'orange',
    '00B0F0': 'blue',
    '000000': 'black'
}


cluster_ans = {"label": [], "question": [], "unique_answers": [], "clusters": []}
map_dict = {}
# Loop through the DataFrame and check the corresponding cell color in openpyxl
for i in tqdm(range(len(df))):
    cell = sheet.cell(row=i + 2, column=2)  # Adjust row index if there's a header row
    fill = cell.fill
    #
    # Check if the cell has a fill color
    if fill.fgColor is not None and fill.fgColor.type == 'rgb' and fill.fgColor.rgb is not None:
        rgb = fill.fgColor.rgb[2:]  # Get the RGB value (skip the leading 'FF' transparency)
        # Find the color name if it's in the mapping dictionary
        color_name = color_mapping.get(rgb, 'Unknown Color')
        # if color_name not in map_dict:
        #     map_dict[color_name] = [df["question"][i]]
        # else:
        #     map_dict[color_name].append(df["question"][i])

        # if color_name == "yellow":
        #     print(f"LLM request sent")
    # op = system_prompt(df['question'][i], df['Column1'][i], msg_others_cell)
    # cluster_ans["unique_answers"].append(df['Column1'][i])
    # cluster_ans["clusters"].append(op)
    # cluster_ans["question"].append(df['question'][i])
    # cluster_ans["label"].append(df['Column2'][i])
    # cluster_ans["label"].append(color_name)
        # if color_name == "orange":
        #     col_start = 7
        #     row_index = i
        #     print(f"LLM request sent")
        #     # for col in df.columns[col_start:]:
        #     #     if pd.notna(df.at[row_index, col]) and df.at[row_index, col] != '':
        #     #         op = system_prompt(df['question'][i], df.at[row_index, col], msg_text_to_nums)
        #     #         df.at[row_index, col] = op
        #     ################################
        #     ans = {}
        #     cell_cleaned = re.sub(r'\bnan\b', 'None', cell.internal_value)  # Replace nan with None
        #     for val in eval(cell_cleaned):
        #         op = system_prompt(df['question'][i], val, msg_text_to_nums)
        #         ans[val] = op
        #     #############################
        #     cluster_ans["unique_answers"].append(df['Column1'][i])
        #     cluster_ans["clusters"].append(ans)
        #     cluster_ans["question"].append(df['question'][i])
        #     cluster_ans["label"].append(color_name)


cluster_df = pd.DataFrame(cluster_ans)
cluster_df.to_excel("clusters6.xlsx", index=False)
# with open("high_level_map.json", "w") as f:
#     json.dump(map_dict, f)
