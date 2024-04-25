import pandas as pd

# Load the CSV data
df = pd.read_csv('./updated_file.csv')

# Select the columns
selected_columns = df[[
                        "Latitude",
                        "Longitude",
                        "Scale",
                        "Name of Children",
                        "Guardian Name",
                        "Area",
                        "Weight (kg)",
                        "Height (cm)",
                        "Health Portfolio",
                        "Age (1-11)",
                        "Gender"]]

# Convert to JSON
json_data = selected_columns.to_json(orient='records')

# Write to a file
with open('./project_nurture/public/coordinates.json', 'w') as f:
    f.write(json_data)