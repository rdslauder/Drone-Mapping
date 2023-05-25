# Drone-Mapping

1) This script is designed to take an automated drone mapping flight plan and the images taken during the flight to create the following outputs:

      a) Flight Plan (PreCoordinates)  
         -extract coordinates and store in a CSV
         -convert to British National Grid
         -convert to Well-Known Text
         -create a point shapefile

      b) Drone Images (PostCoordinates)
         -extract coordinates and store in a CSV
         -convert to British National Grid
         -convert to Well-Known Text
         -create a point shapefile

      c) Plots
         -plot PreCoordinates with and without labels
         -plot PostCoordinates with and without labels
         -plot PreCoordinates and PostCoordinates on the same plot, with and without labels

2) There is an option to assess the accuracy of the flight against the flight plan, there are three different paths depending on whether a flight has been completed as planned:

      a) Flight completed as planned
         -the number of images taken match the number of points in the flight plan
         -accuracy assessment runs

      b) Duplicate Images
         -there are more images than points in the flight plan, due to duplicate images being taken, often due to poor weather conditions
         -duplicate images selected by user and then deleted
         -accuracy assessment runs

      c) Flight not completed
         -there are less images than points in the flight plan, therefore the flight plan has not been completed, likely cut short due to poor weather conditions
         -user asked to check for duplicates images and if any, are deleted. If the flight has been cut short it is likely that duplicate images may have been taken also
         -flight plan points that were not capture are selected by the user and then deleted
         -accuracy assessment runs

3) There is an option to rename the images with a batch number prefix: 

      -this is helpful when organising large sets of drone images
      -e.g. can be used when using batches of images for annotating and input as machine-learning training datasets

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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

