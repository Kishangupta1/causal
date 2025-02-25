import pandas as pd
from tqdm import tqdm


def get_key_for_value_in_list(d, search_value):
    for key, value_list in d.items():
        if any(search_value.lower().strip() == value.lower().strip() for value in value_list):
            return key
    return search_value


if __name__ == '__main__':
    filepath = r"op/map_ques.xlsx"
    df = pd.read_excel(filepath)
    map_dict = {}
    for idx in range(len(df)):
        if df['mapping'][idx] not in map_dict:
            map_dict[df['mapping'][idx]] = [df['mapping'][idx], df['question'][idx]]
        else:
            map_dict[df['mapping'][idx]].append(df['question'][idx])

    df2 = pd.read_excel("op/iter_merged_socio_economic_ques.xlsx")
    mapping = []
    for idx in range(len(df2)):
        key = get_key_for_value_in_list(map_dict, df2['question'][idx])
        # key = map_dict.get(df2['question'][idx], None)
        mapping.append(key)

    df2.insert(2, 'mapping', mapping)
    # Save the updated DataFrame back to an Excel file
    output_path = 'op/map_iter_merged_socio_economic_ques.xlsx'  # Replace with desired output file path
    df2.to_excel(output_path, index=False)
