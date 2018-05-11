'''
Import program to pull LogBook Pro data from CSV files into ForeFlight logbook. 

Assumes that Logbook Pro data has been exported into CSV format and Aircraft 
Configuration data has been exported into TAB delmined TXT file for import.
(Not really the best solution but I can work with it.) 

Files are read in individually and then a separate CSV output file is created that 
should match the input template for ForeFlight. Custom fields are handled.

Created on Apr 23, 2018

@author: Jonathan
'''
import csv

# Filepaths for the Logbook Pro files needed for import
lbpLogbookFile = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup\Jonathan_Hughes_Logbook Flight Log _2018_04_22.csv"
lbpAircraftFile = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup\Aircraft Configuration Report.TXT"
importFile = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup\logbook_import.csv"

# Setup a couple of empty arrays
rawLogBookData = [] 
rawAircraftData = []
rawTemplateData = []
aircraftArray = []
logBookArray = []


# Read in the raw logbook file which will be combined with the aircraft data to create a single import file.
def ImportLogBookCSV(logBookFile):
     
    # Open the logbook file. 
    with open(logBookFile) as f:
        logbook = csv.reader(f, delimiter=',')
               
        # Read in each row and fix remarks field which contains commas that shouldn't be treated as delimiters
        for row in logbook:
            
            # The remarks field is the last field in the file (index at 22)
            remarks = row[22]
            
            # add each additional delimited field to the remarks field
            for i in range(23, len(row)):
                remarks = remarks + ',' + row[i]  
               
            # Clear out the original values and resave the remarks field into the last element of the row
            row[23:len(row)] = ''
            row[22] = remarks
            rawLogBookData.append(row)
                                       
    # Make sure the file is closed.                     
    f.close()


def ImportAircraftTXT(aircraftFile):
    
    # Open the logbook file. 
    with open(aircraftFile) as f:
        aircraft = csv.reader(f, delimiter='\t')
               
        # Read in each row and remove rows that aren't data
        for row in aircraft:
            
            # throw out any row that isn't 5 elements long or the label string  
            if len(row) < 5 or row[1] == 'Type': 
                continue
            else:
                # and append the rest to the file
                rawAircraftData.append(row)
                          
    # Make sure the file is closed.                     
    f.close()


def AssembleTemplateData():
    
    # First write out a header for the template
    with open(importFile, 'w', newline='') as f:
        logbookImport = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
     
        logbookImport.writerow(['ForeFlight Logbook Import'])
        logbookImport.writerow([''])
        logbookImport.writerow(['Aircraft Table'])
        logbookImport.writerow(['Text','Text','YYYY','Text','Text','Text','Text',
                                'Text','Text','Boolean','Boolean','Boolean'])
        logbookImport.writerow(['AircraftID','TypeCode','Year','Make','Model',
                                'Category','Class','GearType','EngineType','Complex','HighPerformance','Pressurized'])
        for row in aircraftArray:
            logbookImport.writerow(row)
        
        logbookImport.writerow([''])
        logbookImport.writerow(['Flights Table'])
        logbookImport.writerow(['Date','Text','Text','Text','Text','hhmm','hhmm','hhmm','hhmm','Decimal','Decimal','Decimal','Decimal','Decimal','Decimal','Decimal','Number','Number','Number','Number','Number','Decimal','Decimal','Decimal','Decimal','Decimal','Decimal','Number','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Decimal','Decimal','Decimal','Decimal','Text','Text','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Boolean','Boolean','Boolean','Text','Decimal','Decimal','Number','Date','Boolean','Text'])
        logbookImport.writerow(['Date','AircraftID','From','To','Route','TimeOut','TimeIn','OnDuty','OffDuty','TotalTime','PIC','SIC','Night','Solo','CrossCountry','Distance','DayTakeoffs','DayLandingsFullStop','NightTakeoffs','NightLandingsFullStop','AllLandings','ActualInstrument','SimulatedInstrument','HobbsStart','HobbsEnd','TachStart','TachEnd','Holds','Approach1','Approach2','Approach3','Approach4','Approach5','Approach6','DualGiven','DualReceived','SimulatedFlight','GroundTraining','InstructorName','InstructorComments','Person1','Person2','Person3','Person4','Person5','Person6','FlightReview','Checkride','IPC','[Text]CustomFieldName','[Numeric]CustomFieldName','[Hours]CustomFieldName','[Counter]CustomFieldName','[Date]CustomFieldName','[Toggle]CustomFieldName','PilotComments'])
        
        for row in logBookArray:
            logbookImport.writerow(row)
               
    # Make sure the file is closed.                     
    f.close()


def CreateAircraftList():
    
    # First thing to do is to loop through the rawLogBookData and find each unique registration number.
    # Then look up the aircraft type in the rawAircraftData file and combine them into a single array
    # to be written into the ForeFlight import file.
    for rowLogBook in rawLogBookData:
        
        # index 12 is Type and 13 is registration
        acID = rowLogBook[13]
        acTypeCode = rowLogBook[12]

        # Look in the aircraftArray and see if we already have this aircraft on file.        
        found = False
        for rowAircraft in aircraftArray:
            # if the aircraft ID is already in the list don't continue
            if rowAircraft[0] == acID:  
                found = True   
                break
        
        # If the aircraft is not found and is not one of a few special cases then add it to our list
        if not found and acID not in ['AIRCRAFT IDENT', 'N/A']:
            for rowRawAircraftData in rawAircraftData:
                # Match the type of aircraft with the type of the N-number and add it to our array
                # Some of these attributes will need to be filled in later to have complete records
                if acTypeCode == rowRawAircraftData[0]:
                    acYear = ''
                    acMake = ''
                    acModel = rowRawAircraftData[0]
                    acCategory = rowRawAircraftData[1]
                    # rename a few things to match what is expected
                    if rowRawAircraftData[2] == 'Single-Engine Land':
                        acClass = 'ASEL'
                    elif rowRawAircraftData[2] == 'Multi-Engine Land':
                        acClass = 'AMEL'
                    elif rowRawAircraftData[2] == 'Glider':
                        acClass = 'Glider'
                    else:
                        acClass = 'none'
                    acGearType = ''
                    acEngineType = rowRawAircraftData[4]  # Might need to rename this one, too
                    #acEngineType = 'Piston'
                    acComplex = ''
                    acHiPerf = ''
                    acPressurized = ''
            
            # Add it to the array         
            aircraftArray.append([acID, acTypeCode, acYear, acMake, acModel, acCategory,
                                  acClass, acGearType, acEngineType, acComplex, acHiPerf, acPressurized])


def CreateLogBookList():
    
    # Loop through the logbook (again) and transform the data to match the expected format for import
    for rowLogBook in rawLogBookData:
 
        # Start with date and aircraft N-number. If N-number is N/A then this is a ground only session
        # so there is no from, to, or route.        
        
        # Don't add the labels as they aren't needed 
        if rowLogBook[11] == 'DATE':
            continue
        
        lbDate = rowLogBook[11]
        lbAcID = rowLogBook[13]
        if rowLogBook[14] == 'N/A':
            lbFrom = ''
            lbTo = ''
            lbRoute = ''
        else:
            # Logbook Pro stores the from, to, and route all in one field so we need to parse it 
            # out into three separate fields. I use dashes in my logbook so from is the string 
            # up until the first dash and to is the string after the last dash. Route is the 
            # stuff in between if and only if there are more than one dashes.
            lbFrom = rowLogBook[14][0:rowLogBook[14].find('-')]
            lbTo = rowLogBook[14][rowLogBook[14].rfind('-') + 1:]
            if rowLogBook[14].count('-') > 1:
                lbRoute = rowLogBook[14][rowLogBook[14].find('-') + 1:rowLogBook[14].rfind('-')]
            else:
                lbRoute = ''
        
        # Hopefully, these indexes are consistent with each export. Otherwise, we can figure them out based 
        # on searching for the labels. 
        lbTotalTime = rowLogBook[16]
        lbPIC = rowLogBook[9]
        lbSIC = rowLogBook[10]
        lbNight = rowLogBook[2]
        lbSolo = rowLogBook[8]
        lbCrossCountry = rowLogBook[3]
        lbDayLandings = rowLogBook[0]
        lbNightLandings = rowLogBook[1]
        lbActualInstrument = rowLogBook[5]
        lbSimInstrument = rowLogBook[6]
        lbDualGiven = rowLogBook[18]
        lbDualReceived = rowLogBook[17]
        lbPilotComments = rowLogBook[22]
        
        # Date,AircraftID,From,To,Route,TimeOut,TimeIn,OnDuty,OffDuty,TotalTime,PIC,SIC,Night,Solo,CrossCountry,Distance,DayTakeoffs,DayLandingsFullStop,
        # NightTakeoffs,NightLandingsFullStop,AllLandings,ActualInstrument,SimulatedInstrument,HobbsStart,HobbsEnd,TachStart,TachEnd,Holds,
        # Approach1,Approach2,Approach3,Approach4,Approach5,Approach6,DualGiven,DualReceived,SimulatedFlight,GroundTraining,InstructorName,InstructorComments,
        # Person1,Person2,Person3,Person4,Person5,Person6,FlightReview,Checkride,IPC,[Text]CustomFieldName,[Numeric]CustomFieldName,[Hours]CustomFieldName,
        # [Counter]CustomFieldName,[Date]CustomFieldName,[Toggle]CustomFieldName,PilotComments
        logBookArray.append([lbDate, lbAcID, lbFrom, lbTo, lbRoute, '', '', '', '', lbTotalTime, lbPIC, lbSIC, lbNight, lbSolo, lbCrossCountry, '', lbDayLandings, lbDayLandings,
                             lbNightLandings, lbNightLandings, lbDayLandings + lbNightLandings, lbActualInstrument, lbSimInstrument, '', '', '', '', '',
                             '', '', '', '', '', '', lbDualGiven, lbDualReceived, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', lbPilotComments])

        
if __name__ == '__main__':
   
    ImportLogBookCSV(lbpLogbookFile)
    ImportAircraftTXT(lbpAircraftFile)
    CreateAircraftList()
    CreateLogBookList()
    AssembleTemplateData()
