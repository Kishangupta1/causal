import pandas as pd
from tqdm import tqdm
import config as cfg
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load a pre-trained model from Hugging Face Model Hub
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


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
        merged_slice = merged_row.iloc[3:]
        current_slice = current_row.iloc[3:]

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
    filepath = "op/map_iter_merged_socio_economic_ques.xlsx"
    df = pd.read_excel(filepath)
    context_group = df.groupby('mapping')
    rows_idx_to_drop = []
    merge_ques_with_map = {}
    for group_name, group_df in tqdm(context_group, desc="Processing"):
        if len(group_df.index) > 1:
            merge_rows(df, group_df.index, rows_idx_to_drop, merge_ques_with_map)

    # Drop all other rows in the list
    df.drop(rows_idx_to_drop, inplace=True)

    # write expand_ques_map to json
    with open('merge_ques_with_map.json', 'w') as json_file:
        json.dump(merge_ques_with_map, json_file, indent=4)

    # Save the updated DataFrame back to an Excel file
    output_path = 'op/ques_map_merged_socio_economic_ques.xlsx'  # Replace with desired output file path
    df.to_excel(output_path, index=False)
