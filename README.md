# Logbook-Pro-to-ForeFlight-Import
Python script to import Logbook Pro CSV output file into ForeFlight using CSV import template

Assumes that Logbook Pro data has been exported into CSV format and Aircraft 
Configuration data has been exported into TAB delmined TXT file for import.
(Not really the best solution but I can work with it.) 

Files are read in individually and then a separate CSV output file is created that 
should match the input template for ForeFlight. Custom fields are handled.
