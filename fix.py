import pandas as pd

# Load the Excel file
file_path = 'data/2024/data_all.xlsx'
sheet1 = pd.read_excel(file_path, sheet_name='Class2023 by source_N=3093')
sheet2 = pd.read_excel(file_path, sheet_name='Source1_Qualtrics N=763')

# Create a dictionary from the first sheet with emails as keys and PIDM as values
email_to_pidm = dict(zip(sheet1['PrimaryEmail'], sheet1['PIDM']))
name_to_pidm = dict(zip(sheet1['FirstName'] + " " + sheet1['LastName'], sheet1['PIDM']))


# Function to fill missing PIDM in the second sheet
def fill_missing_pidm(row):
    if pd.isnull(row['PIDM']):
        pidm = email_to_pidm.get(row['Recipient Email'])
        if pd.isnull(pidm):
            name_key = f"{row['FirstName']} {row['LastName']}"
            pidm = name_to_pidm.get(name_key, row['PIDM'])
        return pidm
    return row['PIDM']

# Apply the function to the second sheet
sheet2['PIDM'] = sheet2.apply(fill_missing_pidm, axis=1)

# Save the updated DataFrame back to a new Excel file
output_file_path = 'updated_file.xlsx'  # Replace with your desired output file path
with pd.ExcelWriter(output_file_path) as writer:
    sheet1.to_excel(writer, sheet_name='Sheet1', index=False)
    sheet2.to_excel(writer, sheet_name='Sheet2', index=False)

print("Missing PIDM values filled and saved to", output_file_path)