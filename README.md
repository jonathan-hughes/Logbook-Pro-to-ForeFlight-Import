# Logbook-Pro-to-ForeFlight-Import
Python script to import Logbook Pro CSV output file into ForeFlight using CSV import template. This works for Logbook Pro version 1.16.9 (DB Version: 1017). Other versions may work but have not been tested.

Assumes that Logbook Pro data has been exported into CSV format and Aircraft Configuration data has been exported into TAB delimited TXT file for import. 

## Instructions for use
You'll have to modify the program to point to the **Backup** folder for your Logbook Pro database. By default this is probably **../Documents/My Logbook Pro Files/v1/Backup**. All files needed for import and the output file should be created in this folder.

### Aircraft Configuration Data
From Logbook Pro run the **Aircraft Configuration Spreadsheet** report from the **Reports** menu (under Aircraft). Export to **Tab Delimited File (.TXT)...** (Not really the best solution but I can work with it.) Accept the default filename **Aircraft Configuration Report.TXT**. 

### Logbook Data
From Logbook Pro choose **Export to CSV** from the **File|Export** menu. You can accept the default filename which will be a combination of the logbook name and the date of the export. The program will automatically choose the most recent file ending in .CSV for import. 

Run **LogBookProToForeFlightImport.py** to create the **logbook_import.csv** file suitable for import into the ForeFlight Web interface.

Open a web browser to the ForeFlight Web interface and import the file under the **Logbook|Import** menu. Hopefully, your data will be clean and no warnings or errors will be found. If not, you may have to tweak the output a bit to get it right.

**NB:** You can only do a full import once or you will get duplicate entries. You can do subsequent imports by date range to update your logbook if you want.

Files are read in individually and then a separate .CSV output file is created that should match the input template for ForeFlight. Custom fields are handled.
