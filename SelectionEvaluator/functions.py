# 3 evaluation functions:
# - 1: Model Net Positive
# - 2: Feature Net Positive4
# - 3: Token Comparison (features or models)

import model_eval
import feature_eval
import synonym_compare

print("""This program automates evaluation for the following:
    1: Net Positive Models
    2: Net Positive Features
    3: Token Comparison (may be features or models)
    Please select an evaluation type (1, 2 or 3) or 4 to quit:
      """)

again = 1

while again:
    print("Please select an evaluation type (1, 2 or 3) or 4 to quit:")
    eval_select = input()
    match eval_select:
        case "1":
            W = input("Gross Positive Models -> W/: ")
            N = input("Negative Models -> N/: ")

            net_pos_models = model_eval.model_rewrite(W, N)
            
            result_string = ", ".join(net_pos_models)
            print("Net Positive Models: ", result_string)
        case "2":
            W = input("Gross Positive Features -> W/: ")
            N = input("Negative Features -> N/: ")
            M = input("Applicable Models: ")
            
            net_pos_features = feature_eval.feature_rewrite(W, N, M)
            
            result_string = ", ".join(net_pos_features)
            print("Net Positive Features: ", result_string)
        case "3":
            group1 = input("Grouping 1: ")
            group2 = input("Grouping 2: ")
            M = input("Models: ")
            
            result, removed = synonym_compare.syn_compare(group1, group2, M)
            
            print("Features in both groupings and compatible with models: ", result)
            print("Removed features: ", removed)
        case "4":
            again = 0
        case _:
            print("""Invalid selection. Please select 1, 2 or 3 for one of the following evaluation types:
                1: Net Positive Models
                2: Net Positive Features
                3: Token Comparison (may be features or models)
                4: Quit Program
                  """)

print("Program ended. Goodbye!")
