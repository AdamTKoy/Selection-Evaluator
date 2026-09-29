# Function to convert list of strings (which may incl. synonyms) to set of distinct individual models/features
def build(inputs, df):
    result = set()
    for item in inputs:
        if item[0:2] == "M-" or item[0:2] == "F-":
            individuals = df.loc[df['synonym'] == item, 'members']
            to_add = [x for sublist in individuals for x in sublist]
            result.update(to_add)
        elif "*" in item:   # skip over obsoletes
            continue
        else:   # at this point, individual elements should already be validated
            result.add(item)
    return result