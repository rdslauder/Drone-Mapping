It is recommended that the sets of test data arecduplicated before running the script, so that if any errors occur, the original data set if available to retry.
If the image created and modified date changes when making copies of the datasets, they can be copiedcusing Robocopy on Windows to keep the original timestamps. 
Press Windows key + R. Type “CMD” then enter to open the command line.

Type “Robocopy [directory to be copied] [directory to be copied to] /s
The /s will copy all subdirectories (all folders within the given directory).

Robocopy C:\Users\rober\\DroneMapping\Test_Images C:\Backup /s




1_Standard

-The number of images match the flight plan.
-The entire flight was completed as planned.

2_Duplicate

-The number of images does not match the flight plan.
-Too many images, there are duplicate images.

3_AbandonedFlight

-The number of images does not match the flight plan.
-Not enough images, the flight plan was not completed.
-There are no duplicate images.

4_DuplicateAbandonedFlight

-The number of images does not match the flight plan.
-Not enough images, the flight plan was not completed.
-There are duplicate images.