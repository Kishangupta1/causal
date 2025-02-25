import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg
import random
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load a pre-trained model from Hugging Face Model Hub
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# open prompt files
with open(cfg.question_sim_iter) as f:
    msg_data_ques = json.load(f)


def get_similar_question_idx(question_with_idx):
    # System msg
    msg_list_ques = [json.dumps({"role": "system", "content": msg_data_ques["system"]})]
    # # User msg
    for msg in msg_data_ques["history"]:
        msg_list_ques.append(json.dumps({"role": "user", "content": msg["user"]}))
        msg_list_ques.append(json.dumps({"role": "assistant", "content": msg["assistant"]}))
    aug_msg_list_ques = msg_list_ques + [json.dumps({'role': 'user', 'content': f"{question_with_idx}"})]
    try:
        # res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list_ques})
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': aug_msg_list_ques})
        str_out_hypo = res_hypo.content.decode()
        similar_question_list = json.loads(str_out_hypo.strip())['content']
    except Exception as e:
        similar_question_list = ""
        print(f"can't do with error {e}")
    return similar_question_list


# function to merge rows with overlap check
def merge_rows(df_l, rows_to_merge, rows_idx_to_drop_list, merge_iter_dict):
    # Start with the first row in the list
    merged_row = df_l.loc[rows_to_merge[0]]
    # get all the sentences
    all_sentences = [df_l['question'][rows_to_merge[idx]] for idx in range(len(rows_to_merge))]
    embeddings = model.encode(all_sentences)
    # Iterate through the remaining rows and merge them if there's no overlap
    for idx, row in enumerate(rows_to_merge[1:]):
        current_row = df_l.loc[row]

        # Slice to ignore the first two columns (question and context)
        merged_slice = merged_row.iloc[2:]
        current_slice = current_row.iloc[2:]

        # Check for overlap: find columns that are non-NaN in both rows (ignoring the first two columns)
        overlap = (merged_slice.notna() & current_slice.notna()).any()
        # Check sentence similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[idx+1]])

        # Only merge if there is no overlap and similarity > threshold
        if not overlap and similarity[0][0] > cfg.sent_sim_thres:
            merged_row = merged_row.combine_first(current_row)
            rows_idx_to_drop_list.append(rows_to_merge[idx + 1])  # row idx to drop
            # add to merge dict
            if df['question'][rows_to_merge[0]] not in merge_iter_dict:
                merge_iter_dict[df['question'][rows_to_merge[0]]] = [df['question'][rows_to_merge[0]], df['question'][rows_to_merge[idx + 1]]]
            else:
                merge_iter_dict[df['question'][rows_to_merge[0]]].append(
                    df['question'][rows_to_merge[idx + 1]])  # Add similar question
        else:
            print(f"Skipping merge with row {row} due to overlap: {overlap} and simlarity: {similarity[0][0]}.")

    # Replace the first row with the merged row
    df_l.loc[rows_to_merge[0]] = merged_row


if __name__ == '__main__':
    filepath = "op/merged_socio_economic_ques.xlsx"
    df = pd.read_excel(filepath)
    no_of_iter = 250
    no_of_ques = 15
    # max_ques_to_merge_at_once = no_of_ques/1
    merge_iter_map = {}
    for i in tqdm(range(no_of_iter), desc="Processing"):
        rows_idx_to_drop = []
        # Randomly sample 20 questions along with their indices
        random_questions = random.sample(list(enumerate(df["question"].str.strip())), no_of_ques)
        similar_question_idx = get_similar_question_idx(random_questions)
        try:
            similar_question_idx_list = eval(similar_question_idx)  # Cast str to list
        except Exception as e:
            print(f"Error: {e} for itr: {i}")
            continue
        if isinstance(similar_question_idx_list, list):
            for idx_list in similar_question_idx_list:
                if len(idx_list) > 1:
                    print(f"Merging indices: {idx_list}")
                    print(f"questions: {[df['question'][x] for x in idx_list]}")
                    merge_rows(df, idx_list, rows_idx_to_drop, merge_iter_map)
        else:
            print(f"Can't convert to list: {similar_question_idx}")
        # Drop all other rows in the list
        df.drop(rows_idx_to_drop, inplace=True)
        df.reset_index(drop=True, inplace=True)  # Reset index after dropping rows

    # write expand_ques_map to json
    with open('merge_iter_map.json', 'w') as json_file:
        json.dump(merge_iter_map, json_file, indent=4)

    # Save the updated DataFrame back to an Excel file
    output_path = f"op/iter_merged_socio_economic_ques.xlsx"  # Replace with desired output file path
    df.to_excel(output_path, index=False)

