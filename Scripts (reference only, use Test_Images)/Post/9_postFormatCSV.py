import csv

def postFormatCSV():

# Format PostCoordinates CSV so that the image numbers align with PreCoordinates CSV and can be passed into the accuracy assessment
    # Open the CSV file for reading
    with open('PostCoordinates.csv', 'r') as infile:
        reader = csv.reader(infile)

        # Skip the header row
        header = next(reader)

        # Sort the remaining rows by the first column
        sorted_rows = sorted(reader, key=lambda row: float(row[0]))

    # Open a new file for writing the sorted CSV
    with open('PostCoordinates.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        # Write the header row
        writer.writerow(header)

        # Write the sorted rows
        writer.writerows(sorted_rows)

