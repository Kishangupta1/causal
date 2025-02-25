import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg


# open prompt files
with open(cfg.context_prompt) as f:
    msg_data_con = json.load(f)


def generate_con(sent):
    # System msg
    msg_list_con = [json.dumps({"role": "system", "content": msg_data_con["system"]})]
    # User msg
    for msg in msg_data_con["history"]:
        msg_list_con.append(json.dumps({"role": "user", "content": msg["user"]}))
        msg_list_con.append(json.dumps({"role": "assistant", "content": msg["assistant"]}))
    aug_msg_list_con = msg_list_con + [json.dumps({'role': 'user', 'content': sent})]
    try:
        res = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': aug_msg_list_con})
        str_out = res.content.decode()
        content = json.loads(str_out.strip())['content']  # pick up the content from the JSON result
    except Exception as e:
        content = ""
        print(f"error with {e}")
        pass
    return content


if __name__ == "__main__":
    filepath = r"op/socio_economic.xlsx"
    df = pd.read_excel(filepath)
    context_list = []
    for idx, sent in tqdm(enumerate(df["question"]), desc="Progress"):
        result = generate_con(sent)
        context_list.append(result)

    # Append context in 2nd col
    df.insert(1, 'context', context_list)
    df.to_excel('op/socio_economic_con.xlsx', index=False, engine='xlsxwriter')

