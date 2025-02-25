import json
import requests
import pandas as pd
from tqdm import tqdm
import config as cfg


# open prompt files
with open(cfg.categorical_val) as f:
    msg_categorical_val = json.load(f)


def system_prompt(question, rows_list, msg_data):
    # System msg
    msg_list = [json.dumps({"role": "system", "content": msg_data["system"]})]
    aug_msg_hypo = msg_data['history'][0][
                  'user'] + f"Question: {question} || Answers: {rows_list}"
    msg_list.append(json.dumps({"role": "user", "content": aug_msg_hypo}))
    config = {
  "mirostat_tau": 1,
  "num_ctx": 8000,
  "num_predict": -1,
  "repeat_last_n": 64,
  "repeat_penalty": 1.1,
  "stop": [
    ""
  ],
  "temperature": 0,
  "top_k": 1,
  "top_p": 0.9
}
    try:
        res_hypo = requests.post(cfg.llm_url + cfg.llm_endpoint, data={'messages': msg_list,
                                                                       'configuration': json.dumps(config)})
        str_out = res_hypo.content.decode()
        result = json.loads(str_out.strip())['content']
    except Exception as e:
        result = ""
        print(f"can't do with error {e}")
    return result


if __name__ == '__main__':
    question = "Do you have to serve any loans?"
    ans = """['Yes', ' ', 'No', nan, 'Yes\n', '\nNo\n', 'no', 'yes, for coming here\nQar 2800\nQAR 300', 'no land mortgege', 'yes coming , 7727', 'loan, for coming qatar, QAR 3000 bank (5%) \nQAR 300', 'yes, QAR 3000 bank (5%) \nQAR 400', 'yes, 2954 \nbroker 5%\nQAR 150', 'Yes, 2000 \n5%', 'yes 2409 inerest 3%\nQAR 100', 'yes,  2545 (3%)\nQAR 100', 'yes , 2720 (3%)\nQR 100', 'Yes, 2590 (3%)\nQR 100', 'yes, 3820, (4%) \nQAR 250', 'yes, 4000 (5%)\nQAR 300', 'yes, 3820 (3%)\nQAR 250', 'yes, 2500 (3%)\nQAR 100', 'yes, 3461 (3%)\nQAR 120', 'yes, 2115 (3%)\nQar 150', 'yes, 3181', 'yes, 19740, \nfrom NGO monthly 900\nfor coming qatar\n', 'no, land mortagage\nQAR 700\nfor coming qatar', 'yes, 2142 (3%)\nQAR 150\nfor coming qatar', 'yes, 3214 (3% interest)\nQAR 200\nfor coming qatar', 'no ', 'yes, 2857 (3%)\nQAR 200\nfor coming qatar', 'no, loan from relatives for coming qatar', 'no, sold his shop for coming qatar', 'yes, QAR 9090 \ncoming qatar, QAR 500 interest 5%', 'yes QR 6818, for coming here\n\ninstallment QR 378', 'yes\nQAR 2285 \nLender 10%\nfor coming qatar\nQAR 300', 'yes \nQR 11363\nQR 9900 from bank  interest 14% in ayear\nbrother QAR 2363\nQAR 850', 'NO', 'No loan', 'No Loan', 'Loan, 10 % interest', 'Loan, 3%', 'Loan from friend', 'Loan, double %', 'Loan, 5 %', 'Loan, 10 %', 'Loan, 10%', 'Loan 5 %', 'Loan 5&', 'Loan 10%', 'Loan 3%', 'Loan from relatives', 'Loan from relatives, 10%', 'Loan, 5%', 'Borrowing money', 'Unsure', 'yes']"""
    op = system_prompt(question, ans, msg_categorical_val)
    print(op)
    # filepath = "op/ques_map_merged_socio_economic_ques.xlsx"
    # df = pd.read_excel(filepath)
    # start_col = 6
    # unique_elm_list = []
    # unique_elm_count = []
    # i = 11
    # # for i in tqdm(range(len(df)), desc="Processing"):
    # row = df.iloc[i, start_col:]
    # row_unique_series = row.drop_duplicates()
    # unique_elm_list.append(row_unique_series.tolist())
    # unique_elm_count.append(len(row_unique_series.tolist()))
    # clustered_row = get_clustered_row(row_unique_series.to_list())
    # df.iloc[i] = clustered_row
    #
    # df_un = pd.DataFrame({'Column1': unique_elm_list, 'Column2': unique_elm_count})
    # df_un.to_excel('unique_data.xlsx', index=False)
    # # Save the updated DataFrame back to an Excel file
    # output_path = 'op/clustered_socio_economic_ans.xlsx'  # Replace with desired output file path
    # df.to_excel(output_path, index=False)