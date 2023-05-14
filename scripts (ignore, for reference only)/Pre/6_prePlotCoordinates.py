import os
import geopandas as gpd
import matplotlib.pyplot as plt

# plot coordinates on a figure with labels and save as an image

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
    for x, y, name in zip(gdf.geometry.x, gdf.geometry.y, gdf["Name"]):
        ax.annotate(name, xy=(x, y), xytext=(3, 0), textcoords="offset points", fontsize=4)
    
    # Save the plot as an image file
    plt.savefig(img_file, dpi=300)

    # Show the plot as an image
    #plt.show()

