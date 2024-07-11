import pandas as pd

data_full = pd.read_excel(
    'data/2024/data_all.xlsx',
    sheet_name='Class2023 by source_N=3093',
    index_col='N_Number'
)

data_survey = pd.read_excel(
    'data/2024/data_all.xlsx',
    sheet_name='Source1_Qualtrics N=763',
)
data_survey.set_index(keys='PIDM', inplace=True, drop=False)

data_udaro = pd.read_excel(
    'data/2024/data_all.xlsx',
    sheet_name='Source2_UDARO_Brigid_N=43',
    index_col='N_Number'
)

data_clearinghouse = pd.read_excel(
    'data/2024/data_all.xlsx',
    sheet_name='Source3_Clearinghouse_Lin_N=256',
    index_col='N_Number'
)

# Update the full data sheet with the other sheets. FIRST CHOOSE INDEX.

data_full.update(other=data_clearinghouse, join='left', overwrite=True)
data_full.update(other=data_udaro, join='left', overwrite=True)

data_full.drop_duplicates(subset='PIDM', inplace=True)
data_full.set_index(keys='PIDM', drop=False, inplace=True)

data_full.update(other=data_survey, join='left', overwrite=True)

data_full.to_excel('data/data_updated.xlsx', index=False)
