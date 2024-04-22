import pandas as pd

# Load the CSV data
df = pd.read_csv('/home/hunterhhh412/Local Stuff/Minor 2/Minor_2/minor2final.csv')

# Select the columns
selected_columns = df[["Latitude", "Longitude"]]

# Convert to JSON
json_data = selected_columns.to_json(orient='records')

# Write to a file
with open('/home/hunterhhh412/Local Stuff/Minor 2/Minor_2/malnutrition/public/coordinates.json', 'w') as f:
    f.write(json_data)