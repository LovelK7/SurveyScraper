SURVEYSCRAPER 4.1
User guide · November 2026


ABOUT

SurveyScraper processes cave survey shots from TopoDroid, Qave and PocketTopo. It extracts the main shots, corrects azimuths for magnetic declination, uses Speleoliti Online to calculate the basic dimensions of the cave, and exports the shot table to a CSV file. It replaces processing survey shots by hand in Excel.


SUPPORTED FILES

• TopoDroid (.csv) – the usual export and the raw-data export (one row per measurement). The format is detected automatically.
• PocketTopo (.txt)
• Qave (.srv)

The source program is detected from the file extension.


INTERFACE

• Speleoliti Online – opens Speleoliti Online (https://www.speleo.net/speleoliti/online/app.html) in Google Chrome.
• HR / EN – interface language.
• Main – import, processing and export of survey shots.
• MagDec – magnetic declination calculation.
• Help – this guide.


1. IMPORT SURVEY SHOTS

In the Main tab, click "Open survey file" and choose a file. The program reads the shots, extracts the main shots and uses Speleoliti Online to calculate polygon length, horizontal length, elevation difference and depth. The cave name, output file name and survey date are filled in automatically when the file contains them.

For the TopoDroid raw-data export:
• repeated measurements of the same main shot are averaged,
• splay shots are kept,
• deleted and overshoot measurements are left out.

If a shot is missing, check in TopoDroid whether it was deleted.


2. STATION PREFIX (optional)

In the "Shot prefix" field, enter a prefix to add to station names, e.g. the surveyor's initials ("jd-") or a cave abbreviation ("dc-").

• TopoDroid and Qave: jd-0, jd-1, jd-2 …
• PocketTopo: jd-1.0, jd-1.1, jd-1.2 …
• Splay shots (TopoDroid) keep the asterisk in front: *jd-0, *jd-1 …

A prefix is recommended: without one, Excel reads station names as numbers and drops leading zeros.


3. MAGNETIC DECLINATION (optional)

Enter the declination in decimal degrees directly in the "Magn. declination" field in the Main tab, or calculate it in the MagDec tab:

1) Enter a location (place, town or address, e.g. "Zagreb, Ilica 1") and click "Lookup coordinates". The location is shown on the map and its coordinates are filled in below.

2) You can also enter coordinates manually. In the "Coordinate system" menu, choose:
   • WGS84 – latitude and longitude in decimal degrees, e.g. 45.8150 and 15.9819
   • HTRS96/TM – Northing (N) and Easting (E) in metres, e.g. 5075146 and 459737

3) Choose the model: WMM (2025–2029) or IGRF (1900–2029). If the survey date is outside the WMM range, IGRF is selected automatically.

4) Check the survey date. It is filled in automatically when the file contains it; otherwise today's date is used.

5) Click "Calculate". The declination is retrieved from NOAA Magnetic Field Calculators (https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml), shown to three decimal places, and entered in the Main tab automatically.

Coordinate systems:
• A decimal comma and spaces are accepted (e.g. 45,8150 or 5 075 146).
• Switching the system converts coordinates already entered to the new system.
• HTRS96/TM coordinates are converted to WGS84 inside the program before the calculation, with no internet needed. HTRS96 and WGS84 differ by less than a metre, which does not affect the declination.
• If N and E are swapped, or degrees are entered instead of metres, the program shows an error.


4. CAVE DATA (optional)

On the right side of the Main tab you can enter the cave name, entrance coordinates (X, Y), elevation (Z), output file name and fixed station.

The highest station is set as the fixed station automatically, so "Depth from fixed station" is also the depth of the cave. Changing the fixed station does not currently recalculate the depth.


5. SAVE SETTINGS

After entering a prefix, declination or cave data, click "Save settings" to apply them.


6. EXPORT TO CSV

Click "Export to CSV" and choose where to save the file. The file contains the cave data and the table of main shots.

• "Add original azimuth column" – exports the original azimuths next to the corrected ones. Available once a declination has been applied with "Save settings".
• "Include splays" (TopoDroid only) – also exports splay shots. Off by default because Speleoliti processing does not support splays.


CONTACT

Send bug reports, comments and suggestions to lkukuljan7 (at) gmail.com.
