import pandas as pd
import json
import requests
import config as cfg
import ast
from tqdm import tqdm
import logging
import re
from logging.handlers import RotatingFileHandler
logging.basicConfig(
    handlers=[RotatingFileHandler(cfg.LOG_FILE, maxBytes=cfg.LOG_FILE_MAX_SIZE,
                                  backupCount=cfg.LOG_FILE_BACKUP_COUNT)],
    level=cfg.LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')
logger = logging.getLogger()

with open(cfg.PROMPT, 'r') as f:
    prompt = f.read()


def get_binary_map_from_llm(system="", user="", query=""):
    messages = [json.dumps({'role': 'system', 'content': system}), json.dumps({'role': 'user', 'content': user})]
    result = requests.post(
        f'{cfg.LLM_URL}/{cfg.LLM_ENDPOINT}',
        files={
            'context_file': (None, ''),
        },
        data={
            'configuration': '{"num_ctx": 3000}',
            'messages': messages,
            'context_link': '',
            'history_prev_msg_id': '',
            'query': query
        }
    )
    return result.json()['content']


def get_binary_key(value, mapping):
    if pd.isna(value):
        return value
    for key, val_list in mapping.items():
        if isinstance(value, str):
            value = value.lower().strip()
        if value in val_list:
            return key
    return pd.NA


if __name__ == "__main__":
    unchangeable_rows = ['Country of Origin', 'Age', 'year', 'Gender', 'Marital status', 'Skilled / unskilled?', 'I get paid fairly for the work I do', 'It is easy to take emergency leave', 'I feel safe at my workplace', 'I have realistic targets at work', 'I can get care if I am sick or inured', 'I get enough time to rest', 'I always feel listened too', 'It is easy to get a problem resolved', 'I am treated with respect', 'I have opportunities to get promoted and learn at work', 'I feel appreciated at my workplace', 'I am supported by my work to give my best', 'Are you employed directly by the site you work on or do you work for through an agency/manpower provider?', 'Approximately how many hours would you have worked in a month to earn this?', 'Are you better off in Qatar or in your home country?', 'Country of residence at time of recruitment.', 'Shift \n(What time is the worker scheduled to work?)', 'Site name (What site the worker works on?)', 'How do you feel about your job?']
    map_for_unchangeable_rows = {"Gender": {"Male": ["m", "male"], "Female": ["female"]},
                                 "Are you employed directly by the site you work on or do you work "
                                 "for through an agency/manpower provider?":
                                     {1: ["yes", "direct", "directly"], 0: ["no", "manpower"]},
                                 "Are you better off in Qatar or in your home country?": {
                                     1: "qatar", 0: "home country", 2: "don't know/same"
                                 }
                                 }
    rating_rows = range(16, 28)  # keep only ratings 1, 2, 3, 4, 5
    worker_start_col = 2

    filepath = r"C:\Users\ADMIN\Desktop\work\Train\Causal_LLM\impact\binary_data\ip\Binary_question_final.xlsx"
    df = pd.read_excel(filepath)

    for index, row in tqdm(df.iterrows()):
        if row['question'].strip() in unchangeable_rows:
            if index in rating_rows:
                df.iloc[index, worker_start_col:] = df.iloc[index, worker_start_col:].apply(
                    lambda x: x if isinstance(x, int) else pd.NA
                )
            if row['question'].strip() in map_for_unchangeable_rows:
                df.iloc[index, worker_start_col:] = df.iloc[index, worker_start_col:].apply(
                    lambda x: get_binary_key(x, map_for_unchangeable_rows[row['question'].strip()]))

            continue
        unique_elements = df.iloc[index, worker_start_col:].dropna().unique()
        unique_elements = [elm.lower().strip() if isinstance(elm, str) else elm for elm in unique_elements ]
        unique_elements = list(set(unique_elements))
        try:
            response = get_binary_map_from_llm(user=f"{prompt} Question: {row['question'].strip()} \n Answer:{str(unique_elements)}")
            binary_map = ast.literal_eval(response)
            logger.info(f"Parsing {index}->{row['question']}->response: {binary_map}")
        except Exception as e:
            logger.info(f"Can't parse {index}->{row['question']}->response: {response}")
        df.iloc[index, worker_start_col:] = df.iloc[index, worker_start_col:].apply(lambda x: get_binary_key(x, binary_map))

    # Replace empty strings with NaN
    df.replace(" ", pd.NA, inplace=True)
    # Drop columns where all values are NaN
    df_cleaned = df.dropna(axis=1, how='all')
    df_cleaned.to_excel('op/Modern_day_slavery_binary_8.xlsx', index=False, engine='xlsxwriter')


