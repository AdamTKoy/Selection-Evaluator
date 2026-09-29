# Function to Validate Input
# - identifies synonyms (starting with 'F-' for features or 'M-' for models) and checks against active synonyms
# - discards obsolete tokens (starting with an asterisk)
# - identifies individual feature/models codes and checks against active codes
# - identifies feature groups (4-characters) and checks against active feature groups
#   -> right now, also restricts query to only ONE feature group (may be changed for future enhancements)

def validate(input_set, unique_members, unique_synonyms=None):
    for x in input_set:
        if x[0:2] == "M-" or x[0:2] == "F-":
            if x not in unique_synonyms:
                print("Error: Invalid synonym: ", x)
                return 0
        elif "*" in x:  # ignore obsoletes here, then remove later
            continue
        elif (len(x) == 7):
            if x not in unique_members:
                print("Error: Invalid model/feature: ", x)
                return 0
        elif len(x) == 4:
            if len(input_set) != 1:
                print("Error: FG not allowed with additional arguments: ", input_set)
                return 0
            if x not in unique_members:
                print("Error: Invalid feature group: ", x)
                return 0
        else:
            print("Error: Invalid input: ", x)
            return 0
    return 1