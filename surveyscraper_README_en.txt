SurveyScraper

*************************************************************************************************************

Version 2.2 (September 2023)
Author: Lovel Kukuljan

************************************* WHAT IS SURVEYSCRAPER? ******************************************

SurveyScraper is a simple program that simplifies the processing of cave survey data.
The program loads created tables of measuring shots from TopoDroid or PocketTopo, filters only
main shots and stores them in a new csv file. Then it is possible to easily copy this data to other software 
for calculating the dimensions of a cave. Additional functionality is the calculation of magnetic declination  
and dicrection corrections of shots, according to the selected location, model and date.

*************************************	INSTRUCTIONS FOR USE	************************************

1. Choose the program you used for drawing and from which you created the survey file (TopoDroid or PocketTopo)

2. Open the shots file - .csv file for TopoDroid / .txt file for PocketTopo

3. Define the sign of the points (optional)
	For example, according to the author of the survey (John Doe - "JD") or the name of the cave (Doe's cave - "dc")
	Then, for the first case, the points will get the following sign:
	JD-0 JD-1
	JD-1 JD-2
	...
	or
	JD-1.0 JD-1.1
	JD-1.1 JD-1.2
	...

4. Include magnetic declination (optional). A separate calculation window opens.
	4.1 Enter the location of the cave (e.g. the nearest town or city, place, street)
	4.2 Get coordinates. The search engine will locate the entered place and enter the coordinates in the following 
	two fields (latitude and longitude). The found location will be displayed on a reduced map.
	4.3 Coordinates can be entered independently (WGS84, decimal notation, e.g. 45.123 and 14.123)
	4.4 Select the desired model (default is WMM)
	4.5 Select the date or day, month and year of the survey
	4.6 Calculate. If everything is entered correctly, the magnetic declination will be generated to three decimal places.
	4.7 Apply. The window will close, and the calculated magnetic declinations will be saved and shown on the main screen.

5. Generate CSV - Select a location to store the CSV file, which will automatically receive the suffix "main_shots".
	If the magnetic declination is defined, then it will be included, if not, it will be 0.
	5.1 A message will be printed whether the procedure is successful or not
	5.2 The option to open the generated CSV file will appear

****************************************** CHANGE LANGUAGE ******************************************

The language of the program is changed by the dropdown setting at the top of the main window. The new language is applied
after reopening the program.

************************************************************************************************************

For any comments or suggestions for improvement, feel free to contact me at lkukuljan7 (at) gmail.com

************************************************************************************************************