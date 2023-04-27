import csv
from shapely.geometry import Point

# Convert grid references into WKT

def Pre_BNG_to_WKT():

    # Define the input and output files
    csv_file = 'PreCoordinates.csv'

    # Open the CSV file and read the data
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = [row for row in reader]

    # Convert each row of CSV data to a Point object and then to WKT
    wkt_list = []
    for row in data:
        east = float(row[3])
        north = float(row[4])
        point = Point(east, north)
        wkt = point.wkt
        wkt_list.append(wkt)

    # Add the WKT data to the original CSV data
    headers.append("Geometry")  # Add new column header
    for i, row in enumerate(data):
        row.append(wkt_list[i])

    # Overwrite the original CSV file with the updated data
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
