import os
import exifread
import csv
import pyproj
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import xml.etree.ElementTree as ET
import datetime


######################################

# Convert KMZ mission plan to KML

def preKMZtoKML():
    
    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kmz_file = os.path.join(script_dir, "PreCoordinates.kmz")
    kml_file = os.path.join(script_dir, "PreCoordinates.kml")

    # Extract the KML file from the KMZ file
    with zipfile.ZipFile(kmz_file, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.kml'):
                with zip_ref.open(file_name) as kml_file_in_zip, open(kml_file, 'wb') as kml_file_out:
                    kml_file_out.write(kml_file_in_zip.read())
                    break



#################################

# Extract coordinates (as latitude longitude) from KML, store in CSV

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



############################################

# Convert latitude longitude (EPSG:4326) to British National Grid (EPSG:27700), store as a new column in the same CSV

def preConvertCoordinates():

    # Define input and output CRSs using EPSG codes
    input_crs = pyproj.CRS('EPSG:4326')
    output_crs = pyproj.CRS('EPSG:27700')

    # Define transformer object for converting between input and output CRSs
    transformer = pyproj.Transformer.from_crs(input_crs, output_crs)

    # Open CSV file containing input coordinates
    with open('PreCoordinates.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        output_rows = []
        for row in reader:
            # Extract latitude and longitude coordinates from CSV row
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            
            # Convert coordinates to output CRS
            easting, northing = transformer.transform(lat, lon)
            
            # Add converted coordinates to output row along with the columns from the source CSV
            output_row = {}
            for key in row:
                output_row[key] = row[key]
            output_row['Easting'] = easting
            output_row['Northing'] = northing
            output_rows.append(output_row)

    # Write converted coordinates to new CSV file
    with open('PreCoordinates.csv', mode='w', newline='') as outfile:
        fieldnames = output_rows[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)



##########################

# Convert grid references into WKT

def preCoordinatesWKT27700():

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



#############################

# Create GeoDataFrame and shapefile

def preCreateGeodataframeShapefile():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "PreCoordinates.csv")
    shp_file = os.path.join(script_dir, "PreCoordinates.shp")

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Convert the WKT strings in the 'geometry' column to GeoSeries
    geoms = gpd.GeoSeries.from_wkt(df['Geometry'])

    # Create a GeoDataFrame with the WKT geometries and the original data
    gdf = gpd.GeoDataFrame(df, geometry=geoms)

    # Write the GeoDataFrame to a shapefile
    gdf.to_file(shp_file, driver='ESRI Shapefile')



#############################

# Plot coordinates on a figure with labels and save as an image

def prePlotCoordinatesLabels():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    img_file = os.path.join(script_dir, "PreCoordinatesLabels.png")
    csv_file = os.path.join(script_dir, "PreCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    for x, y, name in zip(gdf.geometry.x, gdf.geometry.y, gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=2)
    
    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # option to show the plot as an image on screen
    # plt.show()



####################################################################################################################################################################
# POST #
####################################################################################################################################################################

# Rename all the images from 1, based on their time/ date of creation. 
# This ensures that the image numbers match up with the flight plan.
# Check that the images have their original creation time in the image metadata.
# When a file is copied, the file's "Created date" becomes the "Modified date" and the current date (when the file is copied) becomes the "Created date".
# This will result in the created date being later than the modified date and they will not sort into their true order of creation.
# An if/ else statement has been added to account for this.
# Will only convert JPEG images, did not include PNG as this will be the format of the exported plots.

def timedRename(): 

    # Get script directory
    script_directory = os.path.dirname(os.path.realpath(__file__))

    # Set the path to the directory containing the files to be renamed
    folder_path = os.path.join(script_directory)

    # Set the starting index
    start_index = 1

    # Create an empty list to store tuples of (filename, creation time)
    files = []

    # Loop through each file in the directory
    for filename in os.listdir(folder_path):
        # Check if the file is an image
        if os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg']:
            # Get the creation time and modified time of the file
            creation_time = os.path.getctime(os.path.join(folder_path, filename))
            modified_time = os.path.getmtime(os.path.join(folder_path, filename))
           # If the modified date is later than the created date (as it should be): append a tuple of (filename, creation time) to the list
            if modified_time > creation_time:
                files.append((filename, creation_time))
            # ELSE If the created date is later than the modified date (as in copied files): append a tuple of (filename, modified time) to the list
            else:
                files.append((filename, modified_time))
            

    # Sort the list based on the creation time in ascending order
    files.sort(key=lambda x: x[1])

    # Loop through the sorted list and rename the files starting from index 1
    for i, (filename, _) in enumerate(files):
        # Set the new filename
        new_filename = str(i+1) + os.path.splitext(filename)[1]

        # Set the paths to the source and destination files
        source_path = os.path.join(folder_path, filename)
        destination_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(source_path, destination_path)



####################################################

# Pull GPS coordinates from image EXIF data (and convert degrees/minutes/seconds to latitude longitude), store in a CSV with image number

def postImagePullCoordinates():

    # get the directory path where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # set the path to the directory containing the images (same as script directory)
    img_dir = script_dir

    # set the path to the output CSV file in the script directory, name output CSV here
    output_file = os.path.join(script_dir, "PostCoordinates.csv")

    # create a list to hold the GPS data for each image
    gps_data_list = []

    # loop through all the image files in the directory
    for filename in os.listdir(img_dir):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            # open the image file for reading
            with open(os.path.join(img_dir, filename), 'rb') as f:
                # read the EXIF metadata from the image file
                exif_tags = exifread.process_file(f)
                # check if the image has GPS data
                if 'GPS GPSLatitude' in exif_tags and 'GPS GPSLongitude' in exif_tags:
                    # extract the GPS latitude, longitude, and altitude from the EXIF data
                    lat_ref = exif_tags['GPS GPSLatitudeRef'].printable
                    lat = exif_tags['GPS GPSLatitude'].values
                    lon_ref = exif_tags['GPS GPSLongitudeRef'].printable
                    lon = exif_tags['GPS GPSLongitude'].values
                    # convert the degrees/minutes/seconds to decimal degrees
                    lat_dec = float(lat[0].num) / float(lat[0].den) + (float(lat[1].num) / float(lat[1].den) / 60) + (float(lat[2].num) / float(lat[2].den) / 3600)
                    lon_dec = float(lon[0].num) / float(lon[0].den) + (float(lon[1].num) / float(lon[1].den) / 60) + (float(lon[2].num) / float(lon[2].den) / 3600)
                    if lon_ref == 'W':  # if longitude is west of Prime Meridian, multiply by -1
                        lon_dec *= -1
                    # remove the file extension from the filename
                    name = os.path.splitext(filename)[0]
                    # append the GPS data to the list
                    gps_data_list.append([name, lat_dec, lon_dec])

    # write the GPS data to the CSV file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # write the header row
        writer.writerow(['Name', 'Latitude', 'Longitude'])
        # write the GPS data for each image
        for row in gps_data_list:
            writer.writerow(row)



##################################

# Convert latitude longitude (EPSG:4326) to British National Grid (EPSG:27700), store as a new column in the same CSV

def postConvertCoordinates():

    # Define input and output CRSs using EPSG codes
    input_crs = pyproj.CRS('EPSG:4326')
    output_crs = pyproj.CRS('EPSG:27700')

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
            easting, northing = transformer.transform(lat, lon)
            
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



##############################

# Convert reprojected coordinates (EPSG:27700) to WKT representation of geometry

def postCoordinatesWKT27700():

    # Define the input and output files
    csv_file = 'PostCoordinates.csv'

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
    headers.append('Geometry')
    for i, row in enumerate(data):
        row.append(wkt_list[i])

    # Write the combined data to the original CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)




#####################################

# Format PostCoordinates CSV so that the image numbers align with PreCoordinates CSV and can be passed into the accuracy assessment

def postFormatCSV():

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


#####################################

# Accuracy assessment, add results into PostCoordinates.csv

def accuracyAssessment():
    # Read in the two CSV files
    df1 = pd.read_csv('PreCoordinates.csv')
    df2 = pd.read_csv('PostCoordinates.csv')

    # Define a function to calculate the distance difference between two points in meters
    def calculate_distance_diff(easting1, northing1, easting2, northing2):
        point1 = Point(easting1, northing1)
        point2 = Point(easting2, northing2)
        return point1.distance(point2)

    # Create a list to store the distance differences
    distance_diffs = []

    # Iterate over the rows in the first CSV file and calculate the distance difference for each row
    for index, row in df1.iterrows():
        easting1, northing1 = row['Easting'], row['Northing']
        easting2, northing2 = df2.loc[index]['Easting'], df2.loc[index]['Northing']
        distance_diff = calculate_distance_diff(easting1, northing1, easting2, northing2)
        distance_diffs.append(distance_diff)

    # Add the distance differences as a new column in the second CSV file
    df2['Distance Difference (m)'] = distance_diffs

    # Write the updated CSV file to disk
    df2.to_csv('PostCoordinates.csv', index=False)



###########################

# Create GeoDataFrame and shapefile

def postCreateGeodataframeShapefile():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "PostCoordinates.csv")
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Convert the WKT strings in the 'geometry' column to GeoSeries
    geoms = gpd.GeoSeries.from_wkt(df['Geometry'])

    # Create a GeoDataFrame with the WKT geometries and the original data
    gdf = gpd.GeoDataFrame(df, geometry=geoms)

    # Write the GeoDataFrame to a shapefile
    gdf.to_file(shp_file, driver='ESRI Shapefile')


###########################

# plot coordinates on a figure with labels and save as an image

def postPlotCoordinatesLabels():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    img_file = os.path.join(script_dir, "PostCoordinatesLabels.png")
    csv_file = os.path.join(script_dir, "PostCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    for x, y, name in zip(gdf.geometry.x, gdf.geometry.y, gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=2)
    
    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # Show the plot as an image
    #plt.show()

####################################

# plot pre coordinates on a figure without labels and save as an image

def postPlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    img_file = os.path.join(script_dir, "PostCoordinates.png")
    csv_file = os.path.join(script_dir, "PostCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    
    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # Show the plot as an image
    #plt.show()

#####################################

# plot post coordinates on a figure without labels and save as an image

def prePlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    img_file = os.path.join(script_dir, "PreCoordinates.png")
    csv_file = os.path.join(script_dir, "PreCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    
    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # option to show the plot as an image on screen
    # plt.show()

#####################################

# Rename images with user inputting the batch number for a prefix, insert "#" between batch number and image number.
# Will only convert JPEG images, did not include PNG as this will be the format of the exported plots.

def batchRename():

    # Get script directory
    script_directory = os.path.dirname(os.path.realpath(__file__))

    # Set the path to the directory containing the files to be renamed
    folder_path = os.path.join(script_directory)

    # Prompt the user to input a prefix
    prefix = input("Enter the batch number: ")

    # Set the starting index
    start_index = 1

    # Loop through each file in the directory
    for i, filename in enumerate(os.listdir(folder_path)):
        # Check if the file is an image
        if os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg']:
            # Set the new filename
            new_filename = prefix + '#' + str(start_index) + '.jpg'

            # Set the paths to the source and destination files
            source_path = os.path.join(folder_path, filename)
            destination_path = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(source_path, destination_path)

            # Increment the index
            start_index += 1


######################################################################################

preKMZtoKML()
prePullCoordinatesKML()
preConvertCoordinates()
preCoordinatesWKT27700()
preCreateGeodataframeShapefile()

timedRename()
postImagePullCoordinates()
postConvertCoordinates()
postCoordinatesWKT27700()
postFormatCSV()
postCreateGeodataframeShapefile()

prePlotCoordinatesLabels()
postPlotCoordinatesLabels()

accuracyAssessment() 
# if indices do not match (number of photos doesn't match the fligh plan), compare the plots to find the duplicate photo.
# input photo number, that photo will be deleted and the accuracy assessment will rerun.

# plot coordinates on a figure without labels and save as an image
prePlotCoordinates()
postPlotCoordinates()

batchRename()




# Print message when coordinate conversion is complete
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print("PRE FLIGHT: ")
print("-The flight plan in the KMZ file has been extracted, converted to British National Grid and WKT, then stored in PreCoordinates CSV.")
print("-Plots of the planned flight coordinates has been saved as images (one labelled, one unlabelled), and a shapefile created for GIS use.")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print("POST FLIGHT: ")
print("-GPS data has been extracted from the images, converted to British National Grid and WKT, then stored in PostCoordinates CSV.")
print("-Plots of the actual image coordinates has been saved as images (one labelled, one unlabelled), and a shapefile created for GIS use.")
print("A flight accuracy assessment has been done and saved as an extra column in PostCoordinates CSV. ")
print("-All drone images renamed with the batch number.")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")
print(" ")