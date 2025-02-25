import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import json


sim_threshold = 0.6


# open prompt files
with open(cfg.get_topic) as f:
    msg_data_clus = json.load(f)
with open(cfg.split_text) as f:
    msg_data_split = json.load(f)


def get_topic(rows_list):
    # System msg
    msg_list_clus = [json.dumps({"role": "system", "content": msg_data_clus["system"]})]
    aug_msg_hypo = msg_data_clus['history'][0][
                  'user'] + f"{rows_list}"
    msg_list_clus.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
    try:
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list_clus})
        str_out_hypo = res_hypo.content.decode()
        topics = json.loads(str_out_hypo.strip())['content']
    except Exception as e:
        topics = ""
        print(f"can't do with error {e}")
    return topics


def split_text(rows_list):
    # System msg
    msg_list_split = [json.dumps({"role": "system", "content": msg_data_split["system"]})]
    aug_msg_hypo = msg_data_split['history'][0][
                  'user'] + f"{rows_list}"
    msg_list_split.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
    try:
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list_split})
        str_out_hypo = res_hypo.content.decode()
        text_parts = json.loads(str_out_hypo.strip())['content']
    except Exception as e:
        text_parts = ""
        print(f"can't do with error {e}")
    return text_parts


def transform_data(series):
    def process_element(element):
        map_idx = []
        if isinstance(element, str):
            for item in re.split(r'[,\n]', element):
                item = item.strip()
                key1 = next((k for k, v in idx_topic.items() if item in v[1]), None)
                map_idx.append(key1)
        else:
            item = str(element)
            key2 = next((k for k, v in idx_topic.items() if item in v[1]), None)
            map_idx.append(key2)
        return map_idx

    # Apply the process_element function to each element in the series
    return series.apply(process_element)


def keep_unique(row):
    # Convert the row to a set to remove duplicates, then convert back to list
    unique_values = pd.unique(row)
    return unique_values


if __name__ == '__main__':
    filepath = "op/ques_map_merged_socio_economic_ques.xlsx"
    df = pd.read_excel(filepath)
    start_col = 3
    end_col = 20
    idx = 144
    row = df.iloc[idx, start_col:]
    row_unique_series = row.drop_duplicates()
    df_no_header = df.iloc[2:, :]
    df_no_header.columns = [None] * df_no_header.shape[1]
    df_unique = df_no_header.apply(keep_unique, axis=1).drop_duplicates()
    split_dict = {"text": [], "split": []}
    row_split_text = []
    split_text_list = row_unique_series.tolist()
    for idx, text in enumerate(split_text_list):
        print(f"{idx}")
        # if idx == 30:
        #     break
        split_parts = split_text(text)
        split_dict["text"].append([text])
        split_dict["split"].append([split_parts])
    dict_df = pd.DataFrame(split_dict)
    dict_df.to_csv("split_dict.csv", index=False)
    split_list = sum(row_unique_series.apply(
        lambda text: [item.strip() for item in re.split(r'[,\n]', text)] if isinstance(text, str) else [str(text)]), [])
    all_variables_unique = set(split_list)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sent_list = list(all_variables_unique)
    embeddings = model.encode(list(sent_list[:4]))
    cosine_sim_matrix = cosine_similarity(embeddings)
    # for _ in range(10):
    sentence_dict = {}
    visited = set()
    # keep similar sents in a dict
    for i in tqdm(range(len(sent_list))):
        if i in visited:
            continue
        similar_sentences = [sent_list[i]]
        visited.add(i)
        for j in range(len(sent_list)):
            if i != j and cosine_sim_matrix[i, j] >= sim_threshold:
                similar_sentences.append(sent_list[j])
                visited.add(j)
        # Use the first sentence as the key for the group
        sentence_dict[sent_list[i]] = similar_sentences
    idx_topic = {}  # map topic to idx/int
    for pos, (key, val) in enumerate((copy.deepcopy(sentence_dict)).items()):
        topic = get_topic(val)
        sentence_dict[topic] = sentence_dict.pop(key)
        idx_topic[pos] = (topic, val)

    # df.iloc[idx, start_col:] = transform_data(df.iloc[idx, start_col:])
    transform_row = transform_data(df.iloc[idx, start_col:])

    df = pd.DataFrame({'Column1': df.iloc[idx, start_col:], 'Column2': transform_row})

    # Write the DataFrame to a CSV file
    df.to_csv('op/test_data.csv', index=False)

    #### DEBUG #########
    with open("cluster_map.json", "w") as f:
        json.dump(sentence_dict, f)
    ####################
    print('here')
