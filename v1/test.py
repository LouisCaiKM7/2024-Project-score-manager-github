import csv

# Data to be written
data = [
    ['Name', 'Age', 'Country'],
    ['John Doe', 29, 'USA'],
    ['Jane Smith', 34, 'UK'],
    ['Emily Davis', 22, 'Canada']
]

# Path to the new CSV file
csv_file_path = 'new_file.csv'

# Writing to the CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"CSV file '{csv_file_path}' has been created and data has been written to it.")
