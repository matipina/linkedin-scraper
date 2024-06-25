import pandas as pd

data_full = pd.read_excel(
    'data/2024/CLASS2023.xlsx',
    sheet_name='Class2023 by source_N=3096',
)
data_full = data_full.dropna(axis='columns', how='all')

data_survey = pd.read_excel(
    'data/2024/CLASS2023.xlsx',
    sheet_name='Source1_Qualtrics N=763'
)
data_survey = data_survey.dropna(axis='columns', how='all')


data_merged = pd.merge(left=data_full, right=data_survey, on='PIDM', how='left')
data_merged = data_merged.dropna(axis='columns', how='all')
data_merged.to_excel('data/2024/CLASS2023_merged.xlsx', index=False)

#print(data_merged.head())
