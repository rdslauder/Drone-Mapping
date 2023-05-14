import os
import zipfile

# Convert KMZ mission plan to KML

def PreKMZtoKML():
    
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
