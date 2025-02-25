import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg


# open prompt files
with open(cfg.question_form_prompt) as f:
    msg_data_ques = json.load(f)


def generate_ques(sent):
    # System msg
    msg_list_ques = [json.dumps({"role": "system", "content": msg_data_ques["system"]})]
    # User msg
    for msg in msg_data_ques["history"]:
        msg_list_ques.append(json.dumps({"role": "user", "content": msg["user"]}))
        msg_list_ques.append(json.dumps({"role": "assistant", "content": msg["assistant"]}))
    aug_msg_list_ques = msg_list_ques + [json.dumps({'role': 'user', 'content': sent})]
    try:
        res = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': aug_msg_list_ques})
        str_out = res.content.decode()
        content = json.loads(str_out.strip())['content']  # pick up the content from the JSON result
    except Exception as e:
        content = ""
        print(f"error with {e}")
        pass
    return content


if __name__ == "__main__":
    filepath = "op/socio_economic_con.xlsx"
    df = pd.read_excel(filepath)
    expand_ques_map = {0: df.at[0, 'question']}
    # Iteratively replace "none" from context and modify the corresponding questions
    for i in tqdm(range(1, len(df)), desc="Progress"):
        if df.at[i, 'context'] == 'none':
            df.at[i, 'context'] = df.at[i-1, 'context']  # Replace "none" with the previous value
            df.at[i, 'question'] = generate_ques(f"question: {df.at[i, 'question']}  || context: {df.at[i, 'context']}")  # Modify the question

        expand_ques_map[i] = df.at[i, 'question']

    # write expand_ques_map to json
    with open('expand_ques_map.json', 'w') as json_file:
        json.dump(expand_ques_map, json_file, indent=4)

    df.to_excel("op/socio_economic_ques.xlsx", index=False, engine='xlsxwriter')
