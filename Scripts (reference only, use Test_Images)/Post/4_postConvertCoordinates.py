import csv
import pyproj

# Convert decimal degrees (EPSG:4326) to British National Grid (EPSG:27700), store as a new column in the same CSV

def postConvertCoordinates():

    # Define input and output CRSs using EPSG codes
    input_crs = pyproj.CRS(init='EPSG:4326')
    output_crs = pyproj.CRS(init='EPSG:27700')

    # Define transformer object for converting between input and output CRSs
    transformer = pyproj.Transformer.from_crs(input_crs, output_crs)

    # Open CSV file containing input coordinates
    with open('PostCoordinates.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        output_rows = []
        for row in reader:
            # Extract latitude and longitude coordinates from CSV row
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            
            # Convert coordinates to output CRS
            easting, northing = transformer.transform(lon, lat)
            
            # Add converted coordinates to output row along with the columns from the source CSV
            output_row = {}
            for key in row:
                output_row[key] = row[key]
            output_row['Easting'] = easting
            output_row['Northing'] = northing
            output_rows.append(output_row)

    # Write converted coordinates to new CSV file
    with open('PostCoordinates.csv', mode='w', newline='') as outfile:
        fieldnames = output_rows[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)
        
# Print message when coordinate conversion is complete
print('Coordinate conversion complete!')
