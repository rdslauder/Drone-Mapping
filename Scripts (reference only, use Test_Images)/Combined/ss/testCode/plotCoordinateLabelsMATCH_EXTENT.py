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
import shutil




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








prePlotCoordinatesLabels()
postPlotCoordinatesLabels()