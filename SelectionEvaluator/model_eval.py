# Function to rewrite gross postiive (W/) & negative (N/) to net positive: Model Version
# Note: this version does not export to file due to the highly simplistic nature of models
import build_set
import data_files
import data_refresh
import pandas as pd
import validate

# TODO: reconfig code to use SQLAlchemy as this is only SQL pull supported by Python
# For now, suppressing warning since we are getting correct results (as of 4/24/2026)
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")
pd.options.mode.chained_assignment = None # this will suppress the warning about modifying a copied slice of a df


def model_rewrite(with_string, not_with_string):
    # pulls fresh data from Hadoop if not yet done today
    # otherwise will do nothing
    data_refresh.check()

    with_string = with_string.upper()
    with_items = [item.strip() for item in with_string.split(',')]

    if not_with_string == "":
        not_with_items = []
    else:
        not_with_string = not_with_string.upper()
        not_with_items = [item.strip() for item in not_with_string.split(',')]

    mdf = pd.read_csv(data_files.mdl_syn_table, dtype=str)
    mmac_df = pd.read_csv(data_files.actv_mmac, dtype=str)

    unique_mdl_syns = set(mdf['synonym'])
    unique_mdls = set(mmac_df['model'])

    validation_set = set(with_items + not_with_items)
    if not validate.validate(validation_set, unique_mdls, unique_mdl_syns):
        return ['Input failed validation'], 'Input failed validation'

    # splits string into list of models that are members of respective synonyms
    mdf['members'] = mdf['members'].apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    # SORT df by list length (decreasing)
    # so that when rebuilding models into synonyms, we favor synonyms that provide the most coverage
    mdf = mdf.sort_values(by='members', key=lambda x: x.apply(len), ascending=False)

    if not_with_items != []:
        negative = build_set.build(not_with_items, mdf)
        gross_positive = build_set.build(with_items, mdf)
        net_positive = gross_positive.difference(negative)
        # And then also need to eliminate anything from net_positive that isn't an active model
        net_positive = net_positive.intersection(unique_mdls)
    else:
        net_positive = build_set.build(with_items, mdf)

    # Convert back to synonyms when possible
    # - go through each row of model dataframe
    # - if ALL members exist in net_postive set, add synonym to set and remove individual members
    for row in mdf.itertuples():
        current = set(mdf.loc[row.Index, 'members'])
        if current.issubset(net_positive):
            net_positive.add(mdf.loc[row.Index, 'synonym'])
            net_positive = net_positive - current

    net_pos_list = list(net_positive)
    sorted_net_pos = sorted(net_pos_list)
    
    return sorted_net_pos