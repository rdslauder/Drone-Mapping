# Drone-Mapping

The GitHub Repository that contains the scripts, data and environment can be found at: https://github.com/rdslauder/DroneMapping


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Four sets of test data are included in the Test_Images folder. Each one represents a different scenario that can happen when mapping:
1_Standard: the number of images match the flight plan. The entire flight was completed as planned.
2_Duplicate: the number of images does not match the flight plan. Too many images, there are duplicate images.
3_AbandonedFlight: the number of images does not match the flight plan. Not enough images, the flight plan was not completed. There are no duplicate images.
4_DuplicateAbandonedFlight: the number of images does not match the flight plan. Not enough images, the flight plan was not completed. There are also duplicate images.

It is recommended that the sets of test data arecduplicated before running the script, so that if any errors occur, the original data set if available to retry.
If the image created and modified date changes when making copies of the datasets, they can be copiedcusing Robocopy on Windows to keep the original timestamps. 
Press Windows key + R. Type “CMD” then enter to open the command line.

Type “Robocopy [directory to be copied] [directory to be copied to] /s
The /s will copy all subdirectories (all folders within the given directory).

Robocopy C:\Users\rober\\DroneMapping\Test_Images C:\Backup /s

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The virtual environment required to run the script can be imported with Anaconda using the environment.yml file

Open Anaconda, activate the environment that came with the repository then open the python terminal via that environment. 
Navigate to the directory of the required test, within each folder there is already a python file. 
The only requirements for the script to work are that there are drone images in JPG/JPEG format, and there is a KMZ file containing the flight plan. 
When the script runs, it will use the images and KMZ file stored in the same directory as the script.

When the terminal is opened via the environment in anaconda, type the following:
Cd [directory]           # Navigate to the directory, copy and paste the directory address in the square brackets
Python masterScript.py   # This runs the script that is already in the directory with the images and KMZ

