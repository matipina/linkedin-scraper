import pandas as pd

data = pd.read_excel('data/Faculty_Missing_Highest_Degree.xlsx')
data['Name'] = data['First Name'] + ' ' + data['Last Name']
data.to_excel('data/Faculty_Missing_Highest_Degree_Scraped.xlsx', index=False)