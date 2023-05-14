from shapely.geometry import Point
import pandas as pd

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
