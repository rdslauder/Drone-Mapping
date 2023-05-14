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
import shutil


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
            if file_name.endswith(".kml"):
                with zip_ref.open(file_name) as kml_file_in_zip, open(kml_file, "wb") as kml_file_out:
                    kml_file_out.write(kml_file_in_zip.read())
                    break



#################################

# Extract coordinates (as latitude longitude) from KML, store in CSV

def prePullCoordinatesKML():

    # Get the path of the KML file in the same directory as the script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    kml_path = os.path.join(dir_path, "PreCoordinates.kml")

    # Create a CSV file to store the latitude and longitude values
    csv_path = os.path.join(dir_path, "PreCoordinates.csv")
    with open(csv_path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Latitude", "Longitude"])

        # Open the KML file
        tree = ET.parse(kml_path)
        root = tree.getroot()

        # Find all Placemark elements
        for placemark in root.findall(".//{http://www.opengis.net/kml/2.2}Placemark"):
            
            # Get the point name from the name element
            name = placemark.find(".//{http://www.opengis.net/kml/2.2}name").text.strip()

            # Check if the name contains "Flight Path", this is the starting point of the flight that is itnegrated into the KML that we do not want pulling into the CSV
            if "Flight Path" in name:
                continue

            # Get the coordinates of the point
            coords_str = placemark.find(".//{http://www.opengis.net/kml/2.2}coordinates").text.strip()
            coords_list = coords_str.split(",")
            latitude = float(coords_list[1])
            longitude = float(coords_list[0])

            # Write the latitude and longitude to the CSV file
            writer.writerow([name, latitude, longitude])



############################################

# Convert latitude longitude (EPSG:4326) to British National Grid (EPSG:27700), store as a new column in the same CSV

def preConvertCoordinates():

    # Define input and output CRSs using EPSG codes
    input_crs = pyproj.CRS("EPSG:4326")
    output_crs = pyproj.CRS("EPSG:27700")

    # Define transformer object for converting between input and output CRSs
    transformer = pyproj.Transformer.from_crs(input_crs, output_crs)

    # Open CSV file containing input coordinates
    with open("PreCoordinates.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        output_rows = []
        for row in reader:
            # Extract latitude and longitude coordinates from CSV row
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            
            # Convert coordinates to output CRS
            easting, northing = transformer.transform(lat, lon)
            
            # Add converted coordinates to output row along with the columns from the source CSV
            output_row = {}
            for key in row:
                output_row[key] = row[key]
            output_row["Easting"] = easting
            output_row["Northing"] = northing
            output_rows.append(output_row)

    # Write converted coordinates to new CSV file
    with open("PreCoordinates.csv", mode="w", newline="") as outfile:
        fieldnames = output_rows[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)



##########################

# Convert grid references into WKT

def preCoordinatesWKT27700():

    # Define the input and output files
    csv_file = "PreCoordinates.csv"

    # Open the CSV file and read the data
    with open(csv_file, "r") as f:
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
    with open(csv_file, "w", newline='') as f:
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
    geoms = gpd.GeoSeries.from_wkt(df["Geometry"])

    # Create a GeoDataFrame with the WKT geometries and the original data
    gdf = gpd.GeoDataFrame(df, geometry=geoms)

    # Write the GeoDataFrame to a shapefile
    gdf.to_file(shp_file, driver="ESRI Shapefile")



#############################

# plot coordinates on a figure with labels and save as an image.
# Label size = 4
# Had to add a hash and number as prefix so that the images are always next to each other.
# Allows user to flick between images and compare without interruption.
# Store the extents in a global variable so that they can be used one all the other plots


def prePlotCoordinatesLabels():
    
    
    global preExtents

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    img_file = os.path.join(script_dir, "#1_PreCoordinatesLabels.png")
    csv_file = os.path.join(script_dir, "PreCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Get the min and max extents of the GeoDataFrame with a 10% buffer
    xmin, ymin, xmax, ymax = gdf.total_bounds
    x_buffer = 0.05 * (xmax - xmin)
    y_buffer = 0.05 * (ymax - ymin)
    preExtents = (xmin - x_buffer, ymin - y_buffer, xmax + x_buffer, ymax + y_buffer)

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    for x, y, name in zip(gdf.geometry.x, gdf.geometry.y, gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=4)

    # Set the axes limits with the buffer
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

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


    # Create an empty list to store tuples of (filename, creation time)
    files = []

    # Loop through each file in the directory
    for filename in os.listdir(folder_path):
        # Check if the file is an image
        if os.path.splitext(filename)[1].lower() in [".jpg", ".jpeg"]:
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
        if filename.endswith(".JPG") or filename.endswith(".JPEG") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            # open the image file for reading
            with open(os.path.join(img_dir, filename), 'rb') as f:
                # read the EXIF metadata from the image file
                exif_tags = exifread.process_file(f)
                # check if the image has GPS data
                if "GPS GPSLatitude" in exif_tags and "GPS GPSLongitude" in exif_tags:
                    # extract the GPS latitude, longitude, and altitude from the EXIF data
                    lat_ref = exif_tags["GPS GPSLatitudeRef"].printable
                    lat = exif_tags["GPS GPSLatitude"].values
                    lon_ref = exif_tags["GPS GPSLongitudeRef"].printable
                    lon = exif_tags["GPS GPSLongitude"].values
                    # convert the degrees/minutes/seconds to decimal degrees
                    lat_dec = float(lat[0].num) / float(lat[0].den) + (float(lat[1].num) / float(lat[1].den) / 60) + (float(lat[2].num) / float(lat[2].den) / 3600)
                    lon_dec = float(lon[0].num) / float(lon[0].den) + (float(lon[1].num) / float(lon[1].den) / 60) + (float(lon[2].num) / float(lon[2].den) / 3600)
                    if lon_ref == "W":  # if longitude is west of Prime Meridian, multiply by -1
                        lon_dec *= -1
                    # remove the file extension from the filename
                    name = os.path.splitext(filename)[0]
                    # append the GPS data to the list
                    gps_data_list.append([name, lat_dec, lon_dec])

    # write the GPS data to the CSV file
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        # write the header row
        writer.writerow(["Name", "Latitude", "Longitude"])
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
    csv_file = "PostCoordinates.csv"

    # Open the CSV file and read the data
    with open(csv_file, "r") as f:
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
    headers.append("Geometry")
    for i, row in enumerate(data):
        row.append(wkt_list[i])

    # Write the combined data to the original CSV file
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)



#####################################

# Format PostCoordinates CSV so that the image numbers align with PreCoordinates CSV and can be passed into the accuracy assessment

def postFormatCSV():

    # Open the CSV file for reading
    with open("PostCoordinates.csv", "r") as infile:
        reader = csv.reader(infile)

        # Skip the header row
        header = next(reader)

        # Sort the remaining rows by the first column
        sorted_rows = sorted(reader, key=lambda row: float(row[0]))

    # Open a new file for writing the sorted CSV
    with open("PostCoordinates.csv", "w", newline='') as outfile:
        writer = csv.writer(outfile)

        # Write the header row
        writer.writerow(header)

        # Write the sorted rows
        writer.writerows(sorted_rows)


################################

def preFormatCSV():

    with open("PreCoordinates.csv", 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    header = data[0]
    sorted_data = sorted(data[1:], key=lambda x: int(x[header.index('Name')]))
    sorted_data.insert(0, header)
    

    with open("PreCoordinates.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sorted_data)


####################################

def deleteOutputsPostDup():


    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # Specify the names of the files to be deleted
    file_names = ["#2_PostCoordinatesLabels.png", "#4_PostCoordinates.png", "#00_CombinedCoordinates.png", "#0_CombinedCoordinatesLabels.png", "PostCoordinates.csv", "PostCoordinates.shp", 
                  "PostCoordinates.dbf", "PostCoordinates.cpg", "PostCoordinates.shx"]

    # Loop through all the files in the directory
    for file_name in os.listdir(dir_path):
        # Check if the file name is in the list of files to be deleted
        if file_name in file_names:
            # Delete the file
            os.remove(os.path.join(dir_path, file_name))

def createOutputsPostDup():
    timedRename()
    postImagePullCoordinates()
    postConvertCoordinates()
    postCoordinatesWKT27700()
    postFormatCSV()
    postCreateGeodataframeShapefile()
    postPlotCoordinatesLabels()
    postPlotCoordinates()
    dualPlotCoordinatesLabels()
    dualPlotCoordinates()
    
    

def deleteOutputsPreDup():


    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # Specify the names of the files to be deleted
    file_names = ["#1_PreCoordinatesLabels.png", "#3_PreCoordinates.png", "#00_CombinedCoordinates.png", "#0_CombinedCoordinatesLabels.png", "PreCoordinates.shp", 
                  "PreCoordinates.dbf", "PreCoordinates.cpg", "PreCoordinates.shx"]

    # Loop through all the files in the directory
    for file_name in os.listdir(dir_path):
        # Check if the file name is in the list of files to be deleted
        if file_name in file_names:
            # Delete the file
            os.remove(os.path.join(dir_path, file_name))

def createOutputsPreDup():
    preCreateGeodataframeShapefile()
    prePlotCoordinatesLabels()
    prePlotCoordinates()
    dualPlotCoordinatesLabels()
    dualPlotCoordinates()




#####################################

# Accuracy assessment, add results into PostCoordinates.csv

def runAccuracyAssessment():


    # Read in the two CSV files
    df1 = pd.read_csv("PreCoordinates.csv")
    df2 = pd.read_csv("PostCoordinates.csv")

    # Define a function to calculate the distance difference between two points in meters
    def calculate_distance_diff(easting1, northing1, easting2, northing2):
        point1 = Point(easting1, northing1)
        point2 = Point(easting2, northing2)
        return point1.distance(point2)

    # Create a list to store the distance differences
    distance_diffs = []

    # Iterate over the rows in the first CSV file and calculate the distance difference for each row
    for index, row in df1.iterrows():
        easting1, northing1 = row["Easting"], row["Northing"]
        easting2, northing2 = df2.loc[index]["Easting"], df2.loc[index]["Northing"]
        distance_diff = calculate_distance_diff(easting1, northing1, easting2, northing2)
        distance_diffs.append(distance_diff)

    # Add the distance differences as a new column in the second CSV file
    df2["Diff (m)"] = distance_diffs

    # Write the updated CSV file to disk, do not include index numbers (index = False)
    df2.to_csv("PostCoordinates.csv", index=False)



######################################

def runFlightPlanAccuracyAssessment():

    global accuracyAssessComplete

    while True:

        print("\n\n\n\n\n" + 
                "Accuracy assessment failed." + "\n" + 
                "There are less captured images than in the flight plan, was the flight completed?" + "\n" + 
                "Before we fix the flight plan, we need to check if any duplicate images were taken during the flight." + "\n"
                "This can happen in windy conditions when the drone has to reposition itself on the flight plan." + "\n"
                "Review the labelled plots and tell me if there are any duplicate images." + "\n" +
                "Tip - follow the flight pattern as the numbers increase, flicking between the pre and post plot, look out for the moment the 'post' numbers not longer match the 'pre' numbers." 
                "\n\n\n\n\n")
        
        # Ask the user if there are any duplicate images
        
        askDupImage = str(input("Are there any duplicate images? "))
        
        if askDupImage in ["Yes", "yes", "Y", "y"]:

            global userDup2
            global dup2
            
            ####################
            
            # Ask the user to input the duplicate image then delete that image

            dupImage = str(input("What is the duplicate image number? "))                  # No file extension as this will be used in printing messages
            dupImageExt = str(dupImage + ".jpg")    
            
            #######  Check if that number is a valid number, is it an image number in the CSV?
    
            dctry_path = os.path.dirname(os.path.realpath(__file__))           # Set the directory location where the images are
    
            while True:                                                        # Infinite loop to reprompt the user if input is incorrect

                if f"{dupImage}.jpg" in os.listdir(dctry_path):                # If the input number matches an image number, break and continue script
                    break

                else:
                    print("That image does not exist.")                        # If the input number does not match, reprompt and update the input image number
                    newImage = input("Enter a different image number: ")
                    dupImage = newImage

            
            dupImageExt = str(dupImage + ".jpg")                     # assign DupImage to DupImageExt again IN CASE it was changed during the checker loop previously
           
            ########################

            # If number is valid, delete

            os.remove(dupImageExt)

            dup2 = dupImage
            userDup2 = True

            ######## Delete all created outputs as these will have to be recreated with the correct images
            deleteOutputsPostDup()
            # Now that the duplicates and newly created outputs have been deleted, recreate outputs using corrected data then run accuracy assessment
            createOutputsPostDup()
            break
        
        elif askDupImage in ["No", "no", "N", "n"]:
            userDup2 = False
            break
        
        else:
            print("Enter yes or no")
    






# Then compare the pre and post CSV and ammend the pre CSV to match the number of rows in the post CSV.
    
    accuracyAssessComplete = False

    
    
# Ask the user if they want to delete individual points or a range of points from the PreCoordinates Flight Plan CSV
# If you completed most of the flight and didn't finish the last few points, then you might want to delete individial points
# If you only completed a fraction of the flight, you don't want to list hundered of points, so instead give the start and end points to delete the entire range

    global soloBulk
    
    print("\n\n\n\n")
    print("Now we know there are no duplicates, we can amend the flight plan coordinates in the PreCoordinates CSV to match the actual number of images taken.")

    while True:

        
        askSoloBulk = str(input("\n\n\n\n\n" + 
                "Do you want to delete individial points (e.g. 1, 2, 3) or a range of points (e.g. 1 to 250) from the preCoordinates flight plan? "))
        
        if askSoloBulk in ["Individual", "individual", "I", "i"]:

            global deletePreSolo


            ############### Check if the number(s) are valid number(s), is it a number in the flight plan within PreCoordinates.csv?

           # Prompt the user for the initial input image number
            image_numbers = input("Enter the flight plan image number(s) to delete (comma-separated): ")
            number_list = [int(num) for num in image_numbers.split(",")]

            with open("PreCoordinates.csv", "r") as csv_file:
                # Read the CSV data into a list of lists
                data = list(csv.reader(csv_file))
                
                # Extract the "Name" column from the data
                csvNames = [int(row[0]) for row in data[1:]]

            # Check if each num value is present in csvNames
            while not all(num in csvNames for num in number_list):
                missing_nums = [num for num in number_list if num not in csvNames]
                print(f"Images {missing_nums} not present in PreCoordinates.csv")
                image_numbers = input("Enter the flight plan image number(s) to delete (comma-separated): ")
                number_list = [int(num) for num in image_numbers.split(",")]

            # Convert the user input into a list of integers
            image_numbers = [int(num.strip()) for num in image_numbers.split(",")]


            # Reassign numbers to deletePreSolo (used to print messages later) in case they have been amended in the loop
            deletePreSolo = image_numbers 

            
            #############################
            
            with open('PreCoordinates.csv', 'r') as csv_file:
                # Read the CSV data into a list of dictionaries
                data = list(csv.DictReader(csv_file))

                # Delete the specified rows from the data
                data = [row for row in data if int(row['Name']) not in image_numbers]

            # Write the updated data back to the CSV file
            with open('PreCoordinates.csv', 'w', newline='') as csv_file:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            soloBulk = False
            break

        
        ########################################################################

        elif askSoloBulk in ["Range", "range", "R", "r"]:
            global deletePreStart
            global deletePreEnd

            ################################### First number to delete in range

            # Prompt the user for the initial input image number
            start_num = input("Enter the first flight plan image number to delete: ")
            deletePreStart = start_num

            ########### Check if this number is present in the PreCoordinates CSV

            with open("PreCoordinates.csv", "r") as csv_file:
                # Read the CSV data into a list of lists
                data = list(csv.reader(csv_file))

                # Extract the "Name" column from the data
                csvNames = [int(row[0]) for row in data[1:]]

            # Check if the input number is present in csvNames
            while int(start_num) not in csvNames:
                print(f"Image {start_num} not present in PreCoordinates.csv")
                start_num = input("Enter a valid flight plan image number to delete: ")

        
            # Reassign numbers to deletePreSolo (used to print messages later) in case they have been amended in the loop
            deletePreStart = start_num

            
            



            ####################################


            # Add function to check whether the users input numbers can be matched with the contents of the PreCoordinates CSV


            ################################################ Last number to delete in range

             # Prompt the user for the initial input image number
            end_num = input("Enter the ending image number to delete: ")
            deletePreEnd = end_num

          

            ###################################

            ########### Check if this number is present in the PreCoordinates CSV

            with open("PreCoordinates.csv", "r") as csv_file:
                # Read the CSV data into a list of lists
                data = list(csv.reader(csv_file))

                # Extract the "Name" column from the data
                csvNames = [int(row[0]) for row in data[1:]]

            # Check if the input number is present in csvNames
            while int(end_num) not in csvNames:
                print(f"Image {end_num} not present in PreCoordinates.csv")
                end_num = input("Enter a valid flight plan image number to delete: ") 

            deletePreEnd = end_num


            ##############################################################

            ####### Delete the range of values using the start and end numbers inputted by the user
            intDeletePreStart = int(deletePreStart)
            intDeletePreEnd = int(deletePreEnd)
            numberRange = list(range(intDeletePreStart, intDeletePreEnd+1))
            
            
            with open('PreCoordinates.csv', 'r') as csv_file:
                # Read the CSV data into a list of dictionaries
                data = list(csv.DictReader(csv_file))

                # Delete the specified rows from the data
                data = [row for row in data if int(row['Name']) not in numberRange]

            # Write the updated data back to the CSV file
            with open('PreCoordinates.csv', 'w', newline='') as csv_file:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)

            soloBulk = True
            break
        
        else:
            print("Enter individual or range")

    # Format the preCoordinates CSV, when rows get deleted the formatting changes and rows are not sorted to align with PostCoordinates

    preFormatCSV()

    # Delete and recreate the outputs that are incorrect now that we have made amends to the preCoordinates CSV, then run accuracy assessment.
    deleteOutputsPreDup()
    createOutputsPreDup()
    runAccuracyAssessment()
    deleteAndRecreateShapefilePost()
    


#####################################

# Define the condition to check if the captured images match the flight plan
# If they match, run the accuracy asssessment
 # If there are more images than points in the flight plan, delete the duplicate and newly created outputs then recreate outputs using corrected data, run acc assessment
 # If fewer images than flight plan, run fixFlightPlan to amend preCoordinates CSV so the accuracy assessment can be done

def checkAccuracyAssessment(): 
    global accuracyAssessComplete                                   # Set a global variable that can be accessed outside of this function and used to print
    global userDup1
    global dup1                                                                # a message if the function is called                 
 

    while True:

        # Read in the two CSV files
        preCoord = pd.read_csv('PreCoordinates.csv')
        postCoord = pd.read_csv('PostCoordinates.csv')
        
        # If the number of images match the flight plan, run the assessment.
        if len(preCoord['Name']) == len(postCoord['Name']):
            
            runAccuracyAssessment()
            deleteAndRecreateShapefilePost()
            accuracyAssessComplete = True
            userDup1 = False
            break
        
        
            
        # If the number of images is greater than the flight plan (duplicates), ask the user to identify image so we can delete and recreate outputs
        elif len(preCoord['Name']) < len(postCoord['Name']):
            print("\n\n\n\n\n" + 
                    "Accuracy assessment failed." + "\n" + 
                    "The number of captured images do not match the flight plan due to duplicate images." + "\n" + 
                    "Review the labelled plots and tell me the number of the duplicate image." + "\n" +
                    "Tip - follow the flight pattern as the numbers increase, flicking between the pre and post plot, look out for the moment the 'post' numbers not longer match the 'pre' numbers." 
                    "\n\n\n\n\n")
            
            # Ask the user to input the duplicate image
            
            dupImage = str(input("What is the duplicate image number? "))                  # No file extension as this will be used in printing messages
            dupImageExt = str(dupImage + ".jpg")                                           # Add the file extension as this will be needed to delete the image

            ###############  Check if that number is a valid number, is it an image in the directory?
    
            dctry_path = os.path.dirname(os.path.realpath(__file__))           # Set the directory location where the images are
    
            while True:                                                        # Infinite loop to reprompt the user if input is incorrect

                if f"{dupImage}.jpg" in os.listdir(dctry_path):                # If the input number matches an image number, break and continue script
                    break

                else:
                    print("That image does not exist.")                        # If the input number does not match, reprompt and update the input image number
                    newImage = input("Enter a different image number: ")
                    dupImage = newImage

            
            dupImageExt = str(dupImage + ".jpg")                     # assign DupImage to DupImageExt again IN CASE it was changed during the checker loop previously
           
            ########################

            # If number is valid, delete
            os.remove(dupImageExt)
            
            dup1 = dupImage
            userDup1 = True
        
        
        ######## Delete all created outputs as these will have to be recreated with the correct images
            deleteOutputsPostDup()
            
        
        # Now that the duplicates and newly created outputs have been deleted, recreate outputs using corrected data then run accuracy assessment
            createOutputsPostDup()
            runAccuracyAssessment()
            deleteAndRecreateShapefilePost()
            accuracyAssessComplete = True
            break



        # The number of images is less than the flight plan, this can happen if the flight was cut short (e.g. due to poor weather conditions).
        # Because poor weather can also result in the drone going off track and taking extra images, we need the user to check the plans for duplicates.
        # If there are duplicates, we can delete them, recreate the correct outputs, then delete any excess rows from the preCoordinates.csv before running the assessment
        
        else:

            runFlightPlanAccuracyAssessment()
            break


            
            
    

#######################

# Ask the user if they want to run an accuracy assessment.
# If no, accuracy assessment skipped.
# If yes, checkAccuracyAssessment run.

def askAccuracyAssessment():
    global assessed                                                    # Set a global variable that can be accessed outside of this function and used to print
                                                                       # a message if the function is called
 
    
    while True:                                                        # Set up infinite loop so we can reprompt the user if they enter invalid input
            askAssess = str(input("Do you want to assess the accuracy of the images against the flight plan? "))              # Ask the user if they want an accuracy assessment, pass input to variable
        
            if askAssess in ["Yes", "yes", "Y", "y"]:                  # User does want to an assessment
                assessed = True                                        # checkAccuracyAssessment will be called so we set the assessed variable to True
                checkAccuracyAssessment()                              # Run the checkAccuracyAssessment function
                break                                                  # Break from infinite loop
            
            elif askAssess in ["No", "no", "N", "n"]:                  # User does not want to batch rename
                assessed = False                                       # checkAccuracyAssessment has not been called so we set the assessed variable to False
                break                                                  # Break from infinite loop
                                                                 
            
            else:                                                     # If the user does not give valid input
                print("Enter yes or no")                              # Reprompt the user with help on what to enter, will not break from loop until valid response given



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


####################################

# Delete the current PostCoordinates shapefile and recreate a new one from the CSV
# This needs to be done after every accuracy assessment
# The shapefile is created before the assessment so it's attribute table will not contain the results of the accuracy assessment
# By recreating the shapefile, it incorporated that new CSV data into it's attribute table

def deleteAndRecreateShapefilePost():

    ########### Delete current PostCoordinates shapefile

   # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Specify the names of the files to be deleted
    file_names = ["PostCoordinates.shp", "PostCoordinates.dbf", "PostCoordinates.cpg", "PostCoordinates.shx"]

    # Loop through all the files in the directory
    for file_name in os.listdir(dir_path):
        # Check if the file name is in the list of files to be deleted
        if file_name in file_names:
            # Delete the file
            os.remove(os.path.join(dir_path, file_name))

    
    ########### Create a new updated shapefile
    
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

# plot coordinates on a figure with labels and save as an image.
# Label size = 4
# Had to add a hash and number as prefix so that they images are always next to each other.
# Allows user to flick between images and compare without interruption.


def postPlotCoordinatesLabels():
    
    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    img_file = os.path.join(script_dir, "#2_PostCoordinatesLabels.png")
    csv_file = os.path.join(script_dir, "PostCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    for x, y, name in zip(gdf.geometry.x, gdf.geometry.y, gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=4)
    
    
    # Set the axes limits
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # option to show the plot as an image on screen
    # plt.show()




####################################

# Plot pre coordinates on a figure without labels and save as an image.
# Had to add a hash and number as prefix so that they images are always next to each other.
# Allows user to flick between images and compare without interruption.

def postPlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    img_file = os.path.join(script_dir, "#4_PostCoordinates.png")
    csv_file = os.path.join(script_dir, "PostCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame with labels
    ax = gdf.plot(markersize=10, color="red")
    
    
    # Set the axes limits
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)


    # Show the plot as an image
    #plt.show()



#####################################

# Plot post coordinates on a figure without labels and save as an image.
# Had to add a hash and number as prefix so that they images are always next to each other.
# Allows user to flick between images and compare without interruption.


def prePlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    img_file = os.path.join(script_dir, "#3_PreCoordinates.png")
    csv_file = os.path.join(script_dir, "PreCoordinates.csv")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)
    df = pd.read_csv(csv_file)

    # Join the GeoDataFrame with the CSV
    gdf = gdf.merge(df, on="Name")

    # Plot the GeoDataFrame
    ax = gdf.plot(markersize=10, color="red")

    # Set the axes limits
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)


    # option to show the plot as an image on screen
    # plt.show()

###########################

# Create a plot that contains both the PreCoordinates and the PostCoordiantes on the same plot for easier point matching

def dualPlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pre_shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    pre_csv_file = os.path.join(script_dir, "PreCoordinates.csv")
    post_shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    post_csv_file = os.path.join(script_dir, "PostCoordinates.csv")
    img_file = os.path.join(script_dir, "#00_CombinedCoordinates.png")

    # Read in the GeoDataFrames
    pre_gdf = gpd.read_file(pre_shp_file)
    pre_df = pd.read_csv(pre_csv_file)
    post_gdf = gpd.read_file(post_shp_file)
    post_df = pd.read_csv(post_csv_file)

    # Join the GeoDataFrames with the CSVs
    pre_gdf = pre_gdf.merge(pre_df, on="Name")
    post_gdf = post_gdf.merge(post_df, on="Name")

    # Plot the GeoDataFrames with labels
    ax = pre_gdf.plot(markersize=10, color="red")
    post_gdf.plot(ax=ax, markersize=10, color="blue")

    # Set the axes limits
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    
#########################################

def dualPlotCoordinatesLabels():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pre_shp_file = os.path.join(script_dir, "PreCoordinates.shp")
    pre_csv_file = os.path.join(script_dir, "PreCoordinates.csv")
    post_shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    post_csv_file = os.path.join(script_dir, "PostCoordinates.csv")
    img_file = os.path.join(script_dir, "#0_CombinedCoordinatesLabels.png")

    # Read in the GeoDataFrames
    pre_gdf = gpd.read_file(pre_shp_file)
    pre_df = pd.read_csv(pre_csv_file)
    post_gdf = gpd.read_file(post_shp_file)
    post_df = pd.read_csv(post_csv_file)

    # Join the GeoDataFrames with the CSVs
    pre_gdf = pre_gdf.merge(pre_df, on="Name")
    post_gdf = post_gdf.merge(post_df, on="Name")

    # Plot the GeoDataFrames with labels
    ax = pre_gdf.plot(markersize=10, color="red")
    post_gdf.plot(ax=ax, markersize=10, color="blue")
    for x, y, name in zip(pre_gdf.geometry.x, pre_gdf.geometry.y, pre_gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=4, color="red")
    for x, y, name in zip(post_gdf.geometry.x, post_gdf.geometry.y, post_gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=4, color="blue")

    # Set the axes limits
    ax.set_xlim(preExtents[0], preExtents[2])
    ax.set_ylim(preExtents[1], preExtents[3])

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

#######################################

# Rename images with user inputting the batch number for a prefix, insert "#" between batch number and image number.
# Will only convert JPEG/ JPG images, did not include PNG as this will be the format of the exported plots.

def batchRename():
    
    global batchNumber
    
    script_directory = os.path.dirname(os.path.realpath(__file__))               # Get script directory

    folder_path = os.path.join(script_directory)                                 # Set the path to the directory containing the files to be renamed

    batchNo = input("Enter the batch number: ")                                   # Prompt the user to input a prefix
    
    batchNumber = batchNo

    start_index = 1                                                              # Set the starting index

    
    for i, filename in enumerate(os.listdir(folder_path)):                       # Loop through each file in the directory
        
        if os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg']:           # Check if the file is an image

            new_filename = batchNo + '#' + str(start_index) + '.jpg'              # Set the new filename

            source_path = os.path.join(folder_path, filename)                    # Set the paths to the source and destination files
            destination_path = os.path.join(folder_path, new_filename)

            os.rename(source_path, destination_path)                             # Rename the file

            start_index += 1                                                     # Increment the index



#####################################

# Ask the user if they want to rename images with a batch number.
# If yes, run the batchRename function.
# If no, skip the batchRename.

def askBatchRename():
    global batched  
    while True:                                                  # set up infinite loop so we can reprompt the user if they enter invalid input
        request = str(input("Do you want to rename the images with a batch number? "))              # Ask the user if they want to batch rename, pass input to variable
        
        if request in ["Yes", "yes", "Y", "y"]:                   # User does want to batch rename
                                                  # Set a global variable that can be accessed outside of this function and used to print a message
            batchRename()                                         # Run the batchRename function
            batched = True                                        # batchRename has been called so we set the batched variable to True
            break                                                 # Break from infinite loop
        
        elif request in ["No", "no", "N", "n"]:                   # User does not want to batch rename
            batched = False                                       # batchRename has not been called so we set the batched variable to False
            break                                                 # Break from infinite loop
        
        else:
            print("Enter yes or no")                              # reprompt the user with help on what to enter, will not break from loop until valid response given



######################################################################################

# Delete any outputs created so far so we do not create them again when we start the process over.

def deleteOutputs():

    # Get the directory path of the current script
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # Specify the file extensions of the files to be deleted
    file_extensions = [".png", ".csv", ".kml"]

    # Loop through all the files in the directory
    for file_name in os.listdir(dir_path):
        # Check if the file has one of the specified extensions
        if any(file_name.endswith(ext) for ext in file_extensions):
            # Delete the file
            os.remove(os.path.join(dir_path, file_name))


###########################################

# Create a folder that can store a copy of the inital outputs created by the script
# This is so that if you make amendments to the files, you will always have a copy of the originals

def createInitalFolder():

    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the name of the new folder
    new_folder_name = "InitialOutputsBackup"

    # Create the new folder
    new_folder_path = os.path.join(script_dir, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)


def copyInitalOutputs():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a new folder
    new_folder_path = os.path.join(script_dir, "InitialOutputsBackup")

    # Define the file extensions to be copied
    file_extensions = (".png", ".csv", ".kml", ".shp", ".dbf", ".cpg", ".shx")

    # Copy files with the specified extensions into the new folder
    for file_name in os.listdir(script_dir):
        if file_name.endswith(file_extensions):
            source_file_path = os.path.join(script_dir, file_name)
            destination_file_path = os.path.join(new_folder_path, file_name)
            shutil.copy(source_file_path, destination_file_path)



##############################



# Create defaults outputs for pre and post: timed rename, CSV with coordinates and grid references, shapefiles, plots of geometry with labels.

def createInitialOutputs():
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
    prePlotCoordinates()
    postPlotCoordinatesLabels()
    postPlotCoordinates()

    dualPlotCoordinatesLabels()
    dualPlotCoordinates()





#############################################

# Print message to give a summary of the outputs created, was accuracy assessment requested, if so was it successful.

def printSummary():

     
    print("\n\n\n\n\n\n\n\n\n\n")

    print("PRE FLIGHT: ")
    print("-The flight plan in the KMZ file has been extracted, converted to British National Grid and WKT, then stored in PreCoordinates CSV.")
    print("-Points saved as shapefile for use in GIS.")
    print("-Plots of the planned flight coordinates have been saved as images (one labelled, one unlabelled), and a shapefile created for GIS use.")

    print("\n\n")

    print("POST FLIGHT: ")
    print("-GPS data has been extracted from the images, converted to British National Grid and WKT, then stored in PostCoordinates CSV.")
    print("-Points saved as shapefile for use in GIS.")
    print("-Plots of the actual image coordinates has been saved as images (one labelled, one unlabelled), and a shapefile created for GIS use.")

    print("\n\n")

    print("Back ups of the initial outputs have been saved in a seperate folder.")

    print("\n\n")



    # Print a different message depending on whether the user has requested an accuracy assessment
    if assessed:
        print("-Accuracy assessment requested.")
    else: 
        print("-Accuracy assessment not requested.")

    # Print a different message depending on whether the accuracy assessment was a success
    if assessed == True and accuracyAssessComplete == True:                            # if the accuracy assessment was requested and it was a success
        print("-Accuracy assessment successful.")
   
   
    if assessed == True and accuracyAssessComplete == True and userDup1 == True:         # if the accuracy assessment requested, duplicates deleted and it was a success
        print(f"-Duplicate image(s) {dup1} deleted. Accuracy assessment successful.")
    
    if assessed == True and accuracyAssessComplete == False and userDup2 == True and soloBulk == False: 
        print("-Not enough images to match the flight plan.")
        print(f"-Duplicate images {dup2} deleted. preCoordinates amended by deleting images {deletePreSolo} to match postCoordinates.")
        print("-Accuracy assessment successful.")
    
    if assessed == True and accuracyAssessComplete == False and userDup2 == True and soloBulk == True: 
        print("-Not enough images to match the flight plan.")
        print(f"-Duplicate images {dup2} deleted. preCoordinates amended by deleting images from {deletePreStart} to {deletePreEnd} to match postCoordinates.")
        print("-Accuracy assessment successful.")

    if assessed == True and accuracyAssessComplete == False and userDup2 == False and soloBulk == False: 
        print("-Not enough images to match the flight plan.")
        print(f"-preCoordinates amended by deleting images {deletePreSolo} to match postCoordinates.")
        print("-Accuracy assessment successful.")
    
    if assessed == True and accuracyAssessComplete == False and userDup2 == False and soloBulk == True: 
        print("-Not enough images to match the flight plan.")
        print(f"-preCoordinates amended by deleting images from {deletePreStart} to {deletePreEnd} to match postCoordinates.")
        print("-Accuracy assessment successful.")
    


    # Print a different message depending on whether the images have been batch renamed or not.
    if batched:
        print(f"-All drone images renamed in order of capture time, with the batch number {batchNumber}.")
    else: 
        print("-All drone images renamed in order of capture time.")

    print("\n\n\n\n\n\n\n\n\n\n")



########################################################

def plotAllCoordinates():
    prePlotCoordinatesLabels()
    prePlotCoordinates()
    postPlotCoordinatesLabels()
    postPlotCoordinates()
    dualPlotCoordinatesLabels()
    dualPlotCoordinates()


####################

def flightCheck():
    # Create defaults outputs for pre and post: timed rename, CSV with coordinates and grid references, shapefiles, plots of geometry with labels.
    createInitialOutputs()
    createInitalFolder()
    copyInitalOutputs()

    # Ask the user if they want to run an accuracy assessment.
    # If no, accuracy assessment skipped.
    # If yes, checkAccuracyAssessment run.
    # checkAccuracyAssessment checks if the captured images match the flight plan, accuracy assessment cannot be done if this is not the case
    # If they match, run the accuracy asssessment, otherwise: delete the duplicate and newly created outputs then recreate outputs using corrected data.
    askAccuracyAssessment() 

    # Plot coordinates on a figure without labels and save as an image.
    #plotAllCoordinates()

    # Ask the user if they want to rename images with a batch number.
    # If yes, run the batchRename function.
    # If no, skip the batchRename. 
    askBatchRename()

    # Print message to give a summary of the outputs created, was accuracy assessment requested, if so was it successful.
    printSummary()

######################################################

flightCheck()

