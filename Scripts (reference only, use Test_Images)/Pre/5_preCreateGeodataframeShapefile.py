import os
import geopandas as gpd
import pandas as pd

# convert GeoDataFrame (CSV with Geometry) into a shapefile

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
