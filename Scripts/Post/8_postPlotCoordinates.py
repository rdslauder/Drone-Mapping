import os
import geopandas as gpd
import matplotlib.pyplot as plt

# plot coordinates on a figure and save as an image

def postPlotCoordinates():

    # Set the file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shp_file = os.path.join(script_dir, "PostCoordinates.shp")
    img_file = os.path.join(script_dir, "PostCoordinates.png")

    # Read in the GeoDataFrame
    gdf = gpd.read_file(shp_file)

    # Plot the GeoDataFrame
    gdf.plot(markersize=10, color="red")
    plt.grid(True, linestyle=':', color='gray', alpha=0.5)

    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # Show the plot as an image if needed
    #plt.show()

