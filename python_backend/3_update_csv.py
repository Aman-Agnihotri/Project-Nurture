import csv

def replace_columns(source_file, target_file):
    # Read the source CSV file
    with open(source_file, 'r') as source:
        source_reader = csv.reader(source)
        source_header = next(source_reader) # Get the header row
        source_data = list(source_reader)

    # Read the target CSV file
    with open(target_file, 'r') as target:
        target_reader = csv.reader(target)
        target_header = next(target_reader) # Get the header row
        target_data = list(target_reader)

    # Find the indices of the columns to replace
    replace_indices = [target_header.index(column) for column in source_header if column in target_header]

    # Replace the columns in the target data with the corresponding columns from the source data
    for target_row, source_row in zip(target_data, source_data):
        for index in replace_indices:
            target_row[index] = source_row[source_header.index(target_header[index])]

    # Write the updated rows to a new CSV file
    with open('updated_file.csv', 'w', newline='') as output:
        writer = csv.writer(output)
        writer.writerow(target_header)
        writer.writerows(target_data)

replace_columns('coordinates_with_city_state.csv', '/home/hunterhhh412/Local Stuff/Minor 2/Minor_2/minor2final.csv')