# Function to rewrite gross postiive (W/) & negative (N/) to net positive: Feature Version
import build_set
from datetime import datetime
import data_files
import data_refresh
import pandas as pd
import time
import validate

# TODO: reconfig code to use SQLAlchemy as this is only SQL pull supported by Python
# For now, suppressing warning since we are getting correct results (as of 4/24/2026)
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")
pd.options.mode.chained_assignment = None # this will suppress the warning about modifying a copied slice of a df


# TODO: modify so that input takes in an entire selection and has to parse out the W/, N/, models
# and matches features/synonyms across W/ & N/ that are in same FG
def feature_rewrite(with_features, not_with_features, model_string):
    # Time functions used only for testing function efficiency
    print("Starting clock inside function...")
    func_time = time.time()

    # pulls fresh data from Hadoop if not yet done today
    # (hard-coded to look for 5/4/26 since no longer have access to database)
    data_refresh.check()

    # allows simplification of W/ without needing to input a N/
    if not_with_features != "":
        not_with_features = not_with_features.upper()
        not_with_items = [item.strip() for item in not_with_features.split(',')]
    else:
        not_with_items = []

    # inputs are not case sensitive
    model_string = model_string.upper()
    with_features = with_features.upper()

    model_items = [item.strip() for item in model_string.split(',')]

    # import feature and model data
    fdf = pd.read_csv(data_files.ftr_syn_table, dtype=str)
    mdf = pd.read_csv(data_files.mdl_syn_table, dtype=str)

    # import mmac data, which includes 'model', 'fg', and 'feature' columns
    mmac_df = pd.read_csv(data_files.actv_mmac, dtype=str)
    unique_mdls = set(mmac_df['model'])

    # check all model inputs against active models
    mdl_validation_set = set(model_items)
    unique_mdl_syns = set(mdf['synonym'])
    if not validate.validate(mdl_validation_set, unique_mdls, unique_mdl_syns):
        return 'Model input failed validation'
    
    # split synonym member single-strings into lists of individual features
    fdf['members'] = fdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])
    mdf['members'] = mdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    models = build_set.build(model_items, mdf)
    # if user inputs a single FG (and need to only allow one)
    # check it against a validation set of all active FGs
    # if it passes, then pull all compatible features 
    if len(with_features) == 4:
        fg_validation_set = set([with_features])

        all_fgs = set(mmac_df['fg'])

        if not validate.validate(fg_validation_set, all_fgs):
            return 'FG input failed validation'
        else:
            all_compat_in_fg = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == with_features)]
            # populate with_items with a list of strings for all compatible features
            with_items = all_compat_in_fg['feature'].astype(str).tolist()
    else:
        with_items = [item.strip() for item in with_features.split(',')]

    # check all feature inputs against active features/synonyms
    # Note: a synonym with an inactive/obsolete member will be allowed (and ignored during analysis)
        # but if an inactive/obsolete feature is entered, it will cause an (expected) error
    ftr_validation_set = set(with_items + not_with_items)
    unique_ftrs = set(mmac_df['feature'])
    unique_ftr_syns = set(fdf['synonym'])
    if not validate.validate(ftr_validation_set, unique_ftrs, unique_ftr_syns):
        return 'Feature input failed validation'
    
    # go through all synonym members and remove features not present in all active features
    fdf['members'] = fdf['members'].apply(lambda item_list: [item for item in item_list if item in unique_ftrs])

    # subtract N/ from W/ to create net_positive set
    gross_positive = build_set.build(with_items, fdf)
    negative = build_set.build(not_with_items, fdf)
    net_positive = gross_positive.difference(negative)

    # check if there's nothing to analyze/return
    if not net_positive:
        return 'No remaining features identified'

    # check that all features belong to same FG
    fgs = set()
    active_ftrs_grps = mmac_df[['feature', 'fg']].drop_duplicates()
    fg_filter = active_ftrs_grps[active_ftrs_grps['feature'].isin(net_positive)]
    fgs.update(fg_filter['fg'].tolist())

    if len(fgs) > 1:
        return 'Error: Multiple feature groups detected'
    elif len(fgs) < 1:
        return 'Error: No matching feature group identified for input.'

    fg = fgs.pop()

    # only grab features that match models and feature group
    filtered = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == fg)]

    compatible = set(filtered['feature'])

    # Need to remove any features in net_positive that are NOT in MMAC but may still be active/non-obsolete features
    # example: 0014BAB has no MMAC records but is an active, non-obsolete feature in the system (as of 10/28/2025)
    compat_not_net_pos = compatible.difference(net_positive) # active/compatible features not allowed in W/
    net_positive = net_positive.intersection(compatible) # removes features with no MMAC

    # check if there's nothing to analyze/return after removing excluded features
    if not net_positive:
        return 'No remaining features identified'

    # we only want synonyms that have at least 1 member from net_positive
    # and do NOT contain any other FG features compatible with models but restricted by inputs
    mask1 = fdf['members'].apply(lambda x: set(x).isdisjoint(compat_not_net_pos))
    mask2 = fdf['members'].apply(lambda x: set(x).intersection(net_positive))
    filtered_df = fdf[mask1 & mask2]

    # it's possible at this point that NO synonyms will work
    if filtered_df.empty:
        net_pos_list = list(net_positive)
        sorted_net_pos = sorted(net_pos_list)
        result_string = ", ".join(sorted_net_pos)
        return result_string

    # adding calculation for # of feature overlap with net_positive (for ranking)
    filtered_df['values'] = filtered_df.apply(lambda row: len(set(row['members']).intersection(net_positive)), axis=1)
    filtered_df = filtered_df.sort_values(by='values', ascending=False)

    # At this point we can save/export all matching synonyms with ranking to Excel file for manual verification of synonym matching
    # - filenames are unique based on current date and time
    # - export file has sheet for results and separate sheet for query info (W/, N/, Models)
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f"SelectionEvaluator/Exports/feature_syononym_report_{current_timestamp}.xlsx"

    with pd.ExcelWriter(
        fn, engine="openpyxl"
    ) as writer:
        filtered_df.to_excel(writer, sheet_name=current_timestamp, index=False)

        meta_df = pd.DataFrame({
            "Property": ["Gross Positive (W/)", "Negative (N/)", "Models"],
            "Value": [with_features, not_with_features, model_string]
        })
        meta_df.to_excel(writer, sheet_name="Query", index=False)

    for row in filtered_df.itertuples():
        current = set(filtered_df.loc[row.Index, 'members'])
        # since we are modifying net_positive, have to keep checking if this synonym's members intersect with net_positive
        # if so, add synonym to net_positive and remove individual members
        if current.intersection(net_positive):
            syn_to_add = filtered_df.loc[row.Index, 'synonym']
            net_positive.add(syn_to_add)
            net_positive = net_positive.difference(current)

    net_pos_list = list(net_positive)
    sorted_net_pos = sorted(net_pos_list)
    result_string = ", ".join(sorted_net_pos)

    print("Query took %s seconds to run. Sending back final result..." % (time.time() - func_time))

    return result_string
