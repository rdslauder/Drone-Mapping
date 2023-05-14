import csv
import os
import xml.etree.ElementTree as ET

# Extract coordinates from KML, store in CSV

def prePullCoordinatesKML():

    # Get the path of the KML file in the same directory as the script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    kml_path = os.path.join(dir_path, 'PreCoordinates.kml')

    # Create a CSV file to store the latitude and longitude values
    csv_path = os.path.join(dir_path, 'PreCoordinates.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Latitude', 'Longitude'])

        # Open the KML file
        tree = ET.parse(kml_path)
        root = tree.getroot()

        # Find all Placemark elements
        for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
            
            # Get the point name from the name element
            name = placemark.find('.//{http://www.opengis.net/kml/2.2}name').text.strip()

            # Check if the name contains "Flight Path", this is the starting point of the flight that is itnegrated into the KML that we do not want pulling into the CSV
            if "Flight Path" in name:
                continue

            # Get the coordinates of the point
            coords_str = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
            coords_list = coords_str.split(',')
            latitude = float(coords_list[1])
            longitude = float(coords_list[0])

            # Write the latitude and longitude to the CSV file
            writer.writerow([name, latitude, longitude])

        
