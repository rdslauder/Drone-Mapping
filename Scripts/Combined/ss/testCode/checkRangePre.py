import csv

start_num = input("Enter the starting image number to delete: ")
end_num = input("Enter the ending image number to delete: ")
intDeletePreStart = int(start_num)
intDeletePreEnd = int(end_num)
numberRange = list(range(intDeletePreStart, intDeletePreEnd+1))

with open('PreCoordinates.csv', 'r') as csv_file:
    # Read the CSV data into a list of dictionaries
    data = list(csv.DictReader(csv_file))
    
    # Extract the "Name" column from the data
    csvNames = [row['Name'] for row in data]
    
    # Delete the specified rows from the data
    csvNames = [row for row in data if int(row['Name']) in numberRange]

    

csvNames = [int(i) for i in csvNames]



print(numberRange)
print(csvNames)

# using set intersection to compare elements
if set(numberRange).intersection(csvNames) == set(numberRange):
    print("All elements in csvNames are present in numberRange")
else:
    print("Not all elements in csvNames are present in numberRange")



