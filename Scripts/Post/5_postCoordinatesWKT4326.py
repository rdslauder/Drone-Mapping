import csv
from shapely.geometry import Point

### Convert coordinates (EPSG:4326) to WKT representation of geometry

def postCoordinatesWKT4326():

    # Define the input and output files
    csv_file = 'PostCoordinates.csv'
    output_file = 'PostCoordinates.csv'

    # Open the CSV file and read the data
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = [row for row in reader]

    # Convert each row of CSV data to a Point object and then to WKT
    wkt_list = []
    for row in data:
        lat = float(row[1])
        lon = float(row[2])
        point = Point(lon, lat)
        wkt = point.wkt
        wkt_list.append(wkt)

    # Add the WKT data to the original CSV data
    for i, row in enumerate(data):
        row.append(wkt_list[i])

    # Write the combined data to a new CSV file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers + ['WKT'])
        writer.writerows(data)
