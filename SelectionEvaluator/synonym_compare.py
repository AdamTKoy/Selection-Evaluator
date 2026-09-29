import build_set
import data_files
import data_refresh
import pandas as pd
import validate


# Function that will determine feature overlap between two GROUPINGS of synonyms/features
def syn_compare(syn1, syn2, models_input):
    data_refresh() # refresh Hadoop data if source data files are older than today (otherwise does nothing)
    
    syn1 = syn1.upper()
    syn2 = syn2.upper()
    syn1_items = [item.strip() for item in syn1.split(',')]
    syn2_items = [item.strip() for item in syn2.split(',')]

    models_input = models_input.upper()
    model_items = [item.strip() for item in models_input.split(',')]

    validation_set = set(syn1_items + syn2_items)
    mdl_validation_set = set(model_items)

    fdf = pd.read_csv(data_files.ftr_syn_table, dtype=str)
    mdf = pd.read_csv(data_files.mdl_syn_table, dtype=str)
    mmac_df = pd.read_csv(data_files.actv_mmac, dtype=str)

    unique_mdls = set(mmac_df['model'])
    unique_mdl_syns = set(mdf['synonym'])

    if not validate(mdl_validation_set, unique_mdls, unique_mdl_syns):
        return ['Model input failed validation'], ['Model input failed validation']

    unique_ftrs = set(mmac_df['feature'])
    unique_ftr_syns = set(fdf['synonym'])
    if not validate(validation_set, unique_ftrs, unique_ftr_syns):
        return ['Feature input failed validation'], ['Feature input failed validation']

    fdf['members'] = fdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])
    mdf['members'] = mdf['members'].astype(str).apply(lambda x: [item.strip() for item in x.split(',') if item.strip()] if x else [])

    syn1_set = build_set(syn1_items, fdf)
    syn2_set = build_set(syn2_items, fdf)

    in_both = syn1_set.intersection(syn2_set)
    removed = syn1_set.symmetric_difference(syn2_set)

    models = build_set(model_items, mdf)

    fgs = set()

    ftr_fg_df = mmac_df[['feature', 'fg']].drop_duplicates()

    input1_filter = ftr_fg_df[ftr_fg_df['feature'].isin(syn1_set)]
    input2_filter = ftr_fg_df[ftr_fg_df['feature'].isin(syn2_set)]

    input1_fgs = set(input1_filter['fg'])
    input2_fgs = set(input2_filter['fg'])
    print("Feature Groups identified in first input: ", input1_fgs)
    print("Feature Groups identified in second input: ", input2_fgs)

    inBoth_filter = ftr_fg_df[ftr_fg_df['feature'].isin(in_both)]

    if inBoth_filter.empty:
        print("No overlapping features detected. Group 1 and Group 2 are distinct.")
        return [],[removed]

    fgs.update(inBoth_filter['fg'].tolist())

    # TODO: Expand for processing of multiple FGs
    if len(fgs) != 1:
        return ['Multiple FGs detected.'], ['Multiple FGs detected.']

    fg = fgs.pop()
    
    filtered = mmac_df[(mmac_df['model'].isin(models)) & (mmac_df['fg'] == fg)]
    compatible = set(filtered['feature'])

    # remove anything from in_both that isn't also in compatible (has no MMAC for models)
    in_both = in_both.intersection(compatible)

    result_list = list(in_both)
    sorted_result = sorted(result_list)
    result_string = ", ".join(sorted_result)

    removed_list = list(removed)
    sorted_removed = sorted(removed_list)
    removed_string = ", ".join(sorted_removed)

    return result_string, removed_string