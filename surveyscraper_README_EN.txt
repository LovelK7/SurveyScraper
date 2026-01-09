************************************************************************************

		    SurveyScraper - Version 3.2 (January 2026)

************************************************************************************
************************     WHAT IS SURVEYSCRAPER?      ***************************

SurveyScraper is a program that simplifies the processing of survey shot data obtained from the most commonly used digital cave surveying programs: TopoDroid, Qave, and PocketTopo. The program essentially replaces MS Excel functionality for survey shot processing and uses Speleoliti Online features to calculate basic dimensions of the survey or cave object.

*************************     FEATURES       ***************************************

-- Import survey shots and automatic filtering of main shots.
-- Adding prefix/sign to station names saved in the csv file.
-- Correction of shot azimuths according to entered or calculated magnetic declination.
-- Calculation of magnetic declination for selected location, model and date.
-- Saving data and survey shot table to csv file.
-- Include/exclude splay shots in output csv file (TopoDroid).
-- Additional functionality by opening Speleoliti Online
-- Multi-language interface support (Croatian/English).

*************************      INTERFACE DESCRIPTION        ************************

The program consists of a TOP BAR:
-- Speleoliti Online: opens Google Chrome browser and Speleoliti Online page 		(https://www.speleo.net/speleoliti/online/app.html),
-- HR/EN: language selection (Croatian or English),
and THREE TABS:
-- Main: survey shot processing,
-- MagDec: magnetic declination calculation,
-- Help: opens these instructions within the program.

*************************     USER INSTRUCTIONS       ******************************

1. IMPORT 
-- In the Main tab, open the file with shots: TopoDroid csv file, Qave srv file 	or PocketTopo txt file.

2. Define station prefix/sign (optional) 
-- For example, according to the survey author (John Doe - "jd-") or cave name (Doe Cave - "dc-"). Then for TopoDroid and Qave cases, stations will be named:
	jd-0	jd-1
	jd-1	jd-2
	...
-- For PocketTopo:
	jd-1.0	jd-1.1
	jd-1.1	jd-1.2
	...
-- NOTE: For TopoDroid, splay shots are marked with an asterisk (*) which will 	always remain in the first position. For example, prefix "az_" will produce:
	Main shots: az_0, az_1, az_2...
	Splay shots: *az_0, *az_1, *az_2...

3. Enter magnetic declination in decimal degrees or calculate it automatically (optional)
-- 3.1 To calculate magnetic declination, click the MagDec tab
-- 3.2 Enter the cave object location (e.g., nearest place or city, town, street)
-- 3.3 Get coordinates. The search will locate the entered place and enter 		coordinates in the next two fields (latitude and longitude). The found location 	will be displayed on a small map.
-- 3.4 Coordinates can also be entered manually (WGS84, decimal notation with 		dot, e.g. 45.12345 and 14.12345)
-- 3.5 Select the desired model for magnetic declination calculation (default: WMM)
-- 3.6 Select the date - day, month and year of survey (default: today's date)
-- 3.7 Calculate. If everything is entered correctly, magnetic declination will be 	retrieved to three decimal places from the Magnetic Field Calculators portal 		(NOAA, https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml). After 		calculation, the magnetic declination will be automatically entered in the 		magnetic correction field in the Main tab.

4. Enter additional data about the cave object (optional)
-- The right side of the Main window allows entry of object name, entrance 		coordinates and elevation, defining the output file name, and defining the fixed 	station.
-- During shot processing, the highest elevation point is determined as the fixed 	station, whereby the "Depth from fixed station" measure also becomes the cave 		depth.
(Currently, changing the fixed station will not automatically change the depth)

5. Save settings
-- If a station prefix, magnetic declination and/or other object data have been 	entered, they need to be saved by clicking "Save settings".

6. EXPORT
-- Clicking "Export to CSV" opens a window to select the location for saving the 	csv file. The output file consists of rows with object data and a table of main 	survey shots.
-- Option "Add original azimuth column" - If magnetic declination is defined, it 	is possible to activate the option to export a column of original azimuths.
-- Option "Include splays" (TopoDroid) - Enables export of CSV file that includes 	splay shots in addition to main shots. By default it is disabled because 		Speleoliti processing does not support splay shots.

*******************************     CONTACT	 ***********************************

For all bug reports, comments and suggestions for improvement, feel free to contact me at lkukuljan7 (at) gmail.com.		

************************************************************************************
