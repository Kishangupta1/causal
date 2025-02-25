import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load a pre-trained model from Hugging Face Model Hub
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# open prompt files
with open(cfg.question_sim) as f:
    msg_data_ques = json.load(f)
    
    
def get_similar_question_idx(idx, question_list):
    # System msg
    msg_list_ques = [json.dumps({"role": "system", "content": msg_data_ques["system"]})]
    aug_msg_hypo = msg_data_ques['history'][0][
                  'user'] + f"{list(zip(idx, question_list))}"
    msg_list_ques.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
    try:
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list_ques})
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
    all_sentences = [df_l['question'][rows_to_merge[i]] for i in range(len(rows_to_merge))]
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

# def merge_rows(df, rows_to_merge, rows_idx_to_drop_list):
#     # Start with the first row in the list
#     merged_row = df.loc[rows_to_merge[0]]
#
#     # Iterate through the remaining rows and merge them
#     for row in rows_to_merge[1:]:
#         merged_row = merged_row.combine_first(df.loc[row])
#
#     # Replace the first row with the merged row
#     df.loc[rows_to_merge[0]] = merged_row
#
#     # Add rows idx to drop
#     rows_idx_to_drop_list.extend(rows_to_merge[1:])


if __name__ == '__main__':
    filepath = "op/socio_economic_ques.xlsx"
    df = pd.read_excel(filepath)
    rows_idx_to_drop = []
    merge_similar_map = {}
    context_group = df.groupby('context')
    for group_name, group_df in tqdm(context_group, desc="Processing"):
        # Access the 'question' column of the group
        similar_question_idx = get_similar_question_idx(group_df.index, group_df['question'])
        similar_question_idx_list = eval(similar_question_idx)
        if isinstance(similar_question_idx_list, list):
            for idx_list in similar_question_idx_list:
                merge_rows(df, idx_list, rows_idx_to_drop, merge_similar_map)
        else:
            print(f"Can't convert to list: {similar_question_idx}")

    # Drop all other rows in the list
    df.drop(rows_idx_to_drop, inplace=True)

    # write expand_ques_map to json
    with open('merge_similar_map.json', 'w') as json_file:
        json.dump(merge_similar_map, json_file, indent=4)

    # Save the updated DataFrame back to an Excel file
    output_path = 'op/merged_socio_economic_ques.xlsx'  # Replace with desired output file path
    df.to_excel(output_path, index=False)

