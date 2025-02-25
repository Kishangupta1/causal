import pandas as pd
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist
import numpy as np

sim_threshold = 0.8

if __name__ == "__main__":
    var_path = r"C:\Users\ADMIN\Desktop\work\Train\Causal_LLM\impact\binary_data\ip\all-hyp-vars-v4.csv"
    file_path = r"C:\Users\ADMIN\Desktop\work\Train\Causal_LLM\impact\binary_data\op\Modern_day_slavery_binary_8.xlsx"
    model = SentenceTransformer('Gameselo/STS-multilingual-mpnet-base-v2')

    df_var = pd.read_csv(var_path)
    df_file = pd.read_excel(file_path)

    var_list = df_var["var"].to_list()
    # Embed the variable
    embeddings_var = model.encode(var_list)
    # Embed question
    question_list = df_file['question'].to_list()
    embeddings_ques = model.encode(question_list)
    similarity_matrix = 1 - cdist(embeddings_ques, embeddings_var, metric='cosine')
    best_match_indices = np.argmax(similarity_matrix, axis=1)
    assert len(var_list) == len(embeddings_var) and len(question_list) == len(embeddings_ques), "len should be same"
    best_match_values = np.max(similarity_matrix, axis=1)
    best_matches = list(zip(best_match_indices, best_match_values))
    best_match = [var_list[idx] if val > sim_threshold else "" for idx, val in best_matches]
    assert len(best_match) == len(question_list), "len should be same"

    df_file.insert(1, 'mapped_variable', best_match)
    df_file.to_excel('op/Modern_day_slavery_binary_mapped_variable_m.xlsx', index=False, engine='xlsxwriter')

