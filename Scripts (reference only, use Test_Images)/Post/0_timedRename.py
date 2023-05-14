import os
import datetime

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
        if os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            # Get the creation time of the file
            creation_time = os.path.getctime(os.path.join(folder_path, filename))
            # Append a tuple of (filename, creation time) to the list
            files.append((filename, creation_time))

    # Sort the list based on the creation time in ascending order
    files.sort(key=lambda x: x[1])

    # Loop through the sorted list and rename the files starting from index 1
    for i, (filename, _) in enumerate(files):
        # Set the new filename
        new_filename = str(i+1) + '.jpeg'  # change file extension to JPEG

        # Set the paths to the source and destination files
        source_path = os.path.join(folder_path, filename)
        destination_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(source_path, destination_path)

# Print a message indicating that the operation is complete
print("All image files in the directory have been renamed based on their earliest time/date to latest time/date and saved with JPEG extension.")
