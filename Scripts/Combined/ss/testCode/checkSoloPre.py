import csv



def checkSoloPre(number):         # We can pass any number or list of numbers into this and it will check if they are in the PreCoordinates CSV

    
    number_list = [int(num) for num in number.split(",")]

    with open("PreCoordinates.csv", "r") as csv_file:
        # Skip the first row (headers)
        next(csv.reader(csv_file))
        
        # Read the remaining rows of the CSV data into a list of lists
        data = list(csv.reader(csv_file))
        
        # Extract the "Name" column from the data
        csvNames = [int(row[0]) for row in data]

    # Check if each start_num value is present in csvNames
    for number in number_list:
        if number in csvNames:
            print(f"{number} is present in csvNames")
            break
        else:
            print(f"{number} is not present in csvNames")
            number = input("Enter the starting image number(s) to delete (comma-separated): ")
            number_list = [int(num) for num in start_num.split(",")]

    return number    # If the original input number has been amended, this will ensure we return the new updated number


start_num = input("Enter the starting image number to delete: ")    

# Pass start_num into this, the number is checked if it is not present in the PreCoordinates CSV, will reprompt the user until valid input given
# If amended, the number will be returned to replace the old invalid number
start_num = checkSoloPre(start_num)  

