import os
import exifread
import csv

# Pull GPS coordinates from image EXIF data, store in a CSV with image number

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

# print a message to the console when the script is completed
print('GPS data has been extracted from the images and stored in', output_file)