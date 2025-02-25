Run excel_formatting.py -> To convert raw excel data to column wise workers data
context_llm.py -> To assign context to every question
expand_no_context_ques.py -> Expand questions which do not have context by using previous context
merge_similar_ques.py -> group questions based on context and merge similar questions within the group
merge_question_iteratively -> Randomly pick n questions for m iter and merge similar questions
question_map.py -> use a external map .xlxs file and add "mapping" col to the data
merge_question_with_map.py -> group questions based on map and merge similar questons
all_question_map.py -> Map between original and final questions
