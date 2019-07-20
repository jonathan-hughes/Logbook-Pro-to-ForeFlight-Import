'''
Import program to pull LogBook Pro data from CSV files into ForeFlight logbook. 

Assumes that Logbook Pro data has been exported into CSV format and Aircraft 
Configuration data has been exported into TAB delimited TXT file for import.
(Not really the best solution but I can work with it.) 

Files are read in individually and then a separate CSV output file is created that 
should match the input template for ForeFlight. Custom fields are handled.

Created on Apr 23, 2018

@author: Jonathan
'''

import csv
import os

# Filepaths for the Logbook Pro files needed for import
lbpAircraftFile = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup\Aircraft Configuration Report.TXT"
importFile = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup\logbook_import.csv"

# Setup a couple of empty arrays
rawLogBookData = [] 
rawAircraftData = []
rawTemplateData = []
aircraftArray = []
logBookArray = []


def GetLatestCSVFile(csvPath=None):
    
    # If path to CSV files not specified then set to default location 
    if csvPath == None:
        csvPath = r"C:\Users\Jonathan\Documents\My Logbook Pro Files\v1\Backup"

    try:
        # change to the directory
        os.chdir(csvPath)
        
        # get all the files in the directory and then find the last modified file
        # that ends with .csv
        latest = None
        allFiles = os.listdir(csvPath)
        for file in allFiles:
            if file.lower().endswith(".csv"):
                if latest == None:
                    latest = file
                elif os.path.getctime(file) > os.path.getctime(latest):
                    latest = file
                    
        print("Using " + latest + '.')        
        return(latest)

    except Exception as Ex:
        print("Error: " + str(Ex))


# Read in the raw logbook file which will be combined with the aircraft data to create a single import file.
def ImportLogBookCSV(logBookFile):
     
    print('Loading logbook CSV file.') 
    try:
        # Open the logbook file. 
        with open(logBookFile) as f:
            logbook = csv.reader(f, delimiter=',')
                   
            # Read in each row and fix remarks field which contains commas that shouldn't be treated as delimiters
            for row in logbook:
    
                # The remarks field is the last field in the file (index at 22)
                remarks = row[23]
                
                # add each additional delimited field to the remarks field
                for i in range(24, len(row)):
                    remarks = remarks + ',' + row[i]  
                   
                # Clear out the original values and re-save the remarks field into the last element of the row
                row[24:len(row)] = ''
                row[23] = remarks
                
                rawLogBookData.append(row)
    except Exception as Ex:
        print("Error: " + str(Ex))                                  
    
    
def ImportAircraftTXT(aircraftFile):
    
    print('Loading aircraft tab delimited file.')
    try:
        # Open the logbook file. 
        with open(aircraftFile) as f:
            aircraft = csv.reader(f, delimiter='\t')
                   
            # Read in each row and remove rows that aren't data
            for row in aircraft:
                # throw out any row that isn't 5 elements long or the label string  
                if len(row) < 5 or row[0] == 'Type': 
                    continue
                else:
                    # and append the rest to the file
                    rawAircraftData.append(row)

    except Exception as Ex:
        print("Error: " + str(Ex))
                              
    
def AssembleTemplateData():
    
    print('Assembling template data.')
    try:
        # First write out a header for the template
        with open(importFile, 'w', newline='') as f:
            logbookImport = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
         
            logbookImport.writerow(['ForeFlight Logbook Import'] + [''] * 56)
            logbookImport.writerow([''] * 57)
            logbookImport.writerow(['Aircraft Table'] + [''] * 56)
            logbookImport.writerow(['Text',      'Text',    'YYYY','Text','Text', 'Text',    'Text', 'Text',    'Text',      'Boolean','Boolean',        'Boolean'] + [''] * 45)
            logbookImport.writerow(['AircraftID','TypeCode','Year','Make','Model','Category','Class','GearType','EngineType','Complex','HighPerformance','Pressurized'] + [''] * 45)
            for row in aircraftArray:
                logbookImport.writerow(row + [''] * 45)
            
            logbookImport.writerow([''] * 57)
            logbookImport.writerow(['Flights Table'] + [''] * 56)
            logbookImport.writerow(['Date','Text',      'Text','Text','Text', 'hhmm',   'hhmm',   'hhmm',  'hhmm',  'hhmm',  'hhmm',   'Decimal',  'Decimal','Decimal','Decimal','Decimal','Decimal',     'Decimal', 'Number',     'Number',             'Number',       'Number',               'Number',     'Decimal',         'Decimal',            'Decimal',   'Decimal', 'Decimal',  'Decimal','Number','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Decimal',  'Decimal',     'Decimal',        'Decimal',       'Text',          'Text',              'Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Packed Detail','Boolean',     'Boolean',  'Boolean','Decimal',          'Decimal',            'Number',         'Decimal',           'Number',       'Text'])
            logbookImport.writerow(['Date','AircraftID','From','To',  'Route','TimeOut','TimeOff','TimeOn','TimeIn','OnDuty','OffDuty','TotalTime','PIC',    'SIC',    'Night',  'Solo',   'CrossCountry','Distance','DayTakeoffs','DayLandingsFullStop','NightTakeoffs','NightLandingsFullStop','AllLandings','ActualInstrument','SimulatedInstrument','HobbsStart','HobbsEnd','TachStart','TachEnd','Holds', 'Approach1',    'Approach2',    'Approach3',    'Approach4',    'Approach5',    'Approach6',    'DualGiven','DualReceived','SimulatedFlight','GroundTraining','InstructorName','InstructorComments','Person1',      'Person2',      'Person3',      'Person4',      'Person5',      'Person6',      'FlightReview','Checkride','IPC',    '[Hours]Aerobatics','[Hours]Ground Given','[Counter]Tows',  '[Hours]X-C > 50 NM','[Counter]Legs','PilotComments'])
            
            for row in logBookArray:
                logbookImport.writerow(row)
    except Exception as Ex:
        print("Error: " + str(Ex))
                   
    
def CreateAircraftList():
    
    print('Creating aircraft list.')
    try:
        # First thing to do is to loop through the rawLogBookData and find each unique registration number.
        # Then look up the aircraft type in the rawAircraftData file and combine them into a single array
        # to be written into the ForeFlight import file.
        for rowLogBook in rawLogBookData:
            
            # index 2 is Type and 1 is registration
            acID = rowLogBook[2]
            acTypeCode = rowLogBook[1]
    
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
                        acModel = rowRawAircraftData[0]
                        acCategory = rowRawAircraftData[1]
                        if rowRawAircraftData[2] == 'Single-Engine Land':
                            acClass = 'ASEL'
                        elif rowRawAircraftData[2] == 'Multi-Engine Land':
                            acClass = 'AMEL'
                        # There is no "Class" for gliders but if Category is Glider make Class Glider as well     
                        elif rowRawAircraftData[1] == 'Glider':
                            acClass = 'Glider'
                        else:
                            acClass = 'none'
                        
                        acMake = ''
                        acGearType = 'FT'
                        acComplex = ''
                        acHiPerf = ''
                        acPressurized = ''
    
                        # rename a few things to match what is expected
                        if rowRawAircraftData[4] == 'Unpowered':
                            acEngineType = 'Non-Powered'    
                        if rowRawAircraftData[4] == 'Piston Aircraft':
                            acEngineType = 'Piston'
    
                        # Model specific things that we know we can go ahead and assign.
                        if acModel == 'ASK-21':
                            acMake = 'Schleicher'
                        elif acModel[0:3] == 'SGS':
                            acMake = 'Schweizer'
                        elif acModel[0:4] == "G103":
                            acMake = 'Grob'
                            if acModel == 'G103 Twin Astir':
                                acGearType = 'RC'
                        elif acModel[0:7] == 'Pegasus':
                            acMake = 'Centrair'
                            acGearType = 'RC'
                        elif acModel in ['Duo Discus', 'Duo Discus X', 'Discus 2b', 'Discus CS']:
                            acMake = 'Shempp Hirth'
                            acGearType = 'RC'
                        elif acModel in ['C150', 'C172', 'C182', 'R182']:
                            acMake = 'Cessna'
                            if acModel == 'R182':
                                acGearType = 'RT'
                                acHiPerf = 'x'
                                acComplex = 'x'
                            if acModel == 'C182':
                                acHiPerf = 'x'
                        elif acModel in ['N2S-4', 'PT-17']:
                            acMake = 'Boeing'
                            acGearType = 'FC'
                            acEngineType = 'Radial'
                            acHiPerf = 'x'
                        elif acModel == 'DA20-A1':
                            acMake = 'Diamond Aircraft'
                        elif acModel == 'DG-300':
                            acMake = 'Glaser-Dirks'
                            acGearType = 'RC'
                        elif acModel in ['DG-1000S', 'DG-1001M', 'DG-505S']:
                            acMake = 'DG'
                            if acModel == 'DG-1001M':
                                acGearType = 'RC'
                            else:
                                acGearType = 'RT'
                        elif acModel == 'P750':
                            acMake = 'Pacific Aerospace Corp LTD'
                            acHiPerf = 'x'
                        elif acModel[0:3] == 'SZD':
                            acMake = 'PZL'
                            if acModel == 'SZD-48-1':
                                acGearType = 'RC'
                            else:
                                acGearType = 'FC'
                        elif acModel == 'CH7B':
                            acMake = 'Bellanca'
                            acGearType = 'FC'
                        elif acModel == 'AA5A':
                            acMake = 'Grumman'
                        elif acModel == 'L8':
                            acMake = 'Luscombe'
                            acGearType = 'FC'
                        elif acModel == 'U15':
                            acMake = 'Phoenix Air SRO'
                            acGearType = 'FC'
                        elif acModel[0:2] == 'PA':
                            acMake = 'Piper'
                            if acModel == 'PA-28R-200':
                                acGearType = 'RT'
                                acComplex = 'x'
                            if acModel in ['PA-28', 'PA-25']:
                                acHiPerf = 'x'
                            if acModel in ['PA-25', 'PA-16']:
                                acGearType = 'FC'    
                        elif acModel == 'M20J':
                            acMake = 'Mooney'
                            acGearType = 'RT'
                            acComplex = 'x'
                        elif acModel == 'FDCT':
                            acMake = 'Flight Design'
                            acGearType = 'FT'
                        elif acModel == 'LS4-a':
                            acMake = 'Rolladen-Schneider'
                            acGearType = 'RC'
                        elif acModel == 'BOLT':
                            acMake = 'Steen Aero Lab'
                            acGearType = 'FC'
                        elif acModel == 'SC01':
                            acMake = 'Gyroflug'
                            acGearType = 'RT'
                        elif acModel == 'LC42-550FG':
                            acMake = 'Lancair'
                            acGearType = 'FT'
                            acHiPerf = 'x'
                        elif acModel == '300L':
                            acMake = 'Extra Flugzeugbau'
                            acGearType = 'FC'
                            acHiPerf = 'x'
                        elif acModel == 'RV6':
                            acMake = 'Van''s Aircraft'
                            acGearType = 'FC'
                        elif acModel[0:3] == 'W10':
                            acMake = 'Wittman'
                            acGearType = 'FC'
                        else:
                            acMake = ''
                        
                        # Add it to the array         
                        aircraftArray.append([acID, acTypeCode, acYear, acMake, acModel, acCategory,
                                      acClass, acGearType, acEngineType, acComplex, acHiPerf, acPressurized])
    except Exception as Ex:
        print("Error: " + str(Ex))
                            
    
def CreateLogBookList():
    
    print('Creating logbook list.')
    try:
        # Loop through the logbook (again) and transform the data to match the expected format for import
        for rowLogBook in rawLogBookData:
     
            # Start with date and aircraft N-number. If N-number is N/A then this is a ground only session
            # so there is no from, to, or route.        
            
            # Don't add the labels as they aren't needed 
            if rowLogBook[0] == 'DATE':
                continue
            
            lbDate = rowLogBook[0]
            lbAcID = rowLogBook[2]
            if rowLogBook[3] == 'N/A':
                lbFrom = ''
                lbTo = ''
                lbRoute = ''
            else:
                # Logbook Pro stores the from, to, and route all in one field so we need to parse it 
                # out into three separate fields. I use dashes in my logbook so from is the string 
                # up until the first dash and to is the string after the last dash. Route is the 
                # stuff in between if and only if there are more than one dashes.
                lbFrom = rowLogBook[3][0:rowLogBook[3].find('-')]
                lbTo = rowLogBook[3][rowLogBook[3].rfind('-') + 1:]
                if rowLogBook[3].count('-') > 1:
                    lbRoute = rowLogBook[3][rowLogBook[3].find('-') + 1:rowLogBook[3].rfind('-')]
                else:
                    lbRoute = ''
            
            # Hopefully, these indexes are consistent with each export. Be sure to compact database before doing the export!
            lbLegs = rowLogBook[4]
            lbTotalTime = rowLogBook[5]
            lbPIC = rowLogBook[15]
            lbSIC = rowLogBook[16]
            lbNight = rowLogBook[8]
            lbSolo = rowLogBook[14]
            lbCrossCountry = rowLogBook[9]
            lbXC50NM = rowLogBook[10]        
            lbDayLandings = rowLogBook[6]
            lbNightLandings = rowLogBook[7]
            if lbNightLandings == '':
                lbDayTakeOffs = lbDayLandings
            lbActualInstrument = rowLogBook[11]
            lbSimInstrument = rowLogBook[12]
            lbDualGiven = rowLogBook[18]
            lbDualReceived = rowLogBook[17]        
            lbGroundGiven = rowLogBook[19]
            lbGroundReceived = rowLogBook[20]
            lbAerobatics = rowLogBook[21]
            lbTows = rowLogBook[22]
            lbPilotComments = rowLogBook[23]        
            
            #                                                                                                                                                                                                                                                                                                                                                                                                      #             type          runway        airport       comments                                                                                                                                                                  name          role          email                                                  
            #                    Date    Text        Text    Text  Text     hhmm     hhmm     hhmm    hhmm    hhmm    hhmm         Decimal      Decimal  Decimal Decimal  Decimal Decimal         Decimal   Number         Number               Number           Number                 Number                           Decimal             Decimal              Decimal     Decimal   Decimal    Decimal  Number Packed Detail Packed Detail Packed Detail Packed Detail Packed Detail Packed Detail Decimal      Decimal         Decimal          Decimal           Text            Text                Packed Detail Packed Detail Packed Detail Packed Detail Packed Detail Packed Detail Boolean       Boolean    Boolean Decimal       Decimal        Number  Decimal      Number  Text
            #                    Date,   AircraftID, From,   To,   Route,   TimeOut, TimeOff, TimeOn, TimeIn, OnDuty, OffDuty,     TotalTime,   PIC,     SIC,    Night,   Solo,   CrossCountry,   Distance, DayTakeoffs,   DayLandingsFullStop, NightTakeoffs,   NightLandingsFullStop, AllLandings,                     ActualInstrument,   SimulatedInstrument, HobbsStart, HobbsEnd, TachStart, TachEnd, Holds, Approach1,    Approach2,    Approach3,    Approach4,    Approach5,    Approach6,    DualGiven,   DualReceived,   SimulatedFlight, GroundTraining,   InstructorName, InstructorComments, Person1,      Person2,      Person3,      Person4,      Person5,      Person6,      FlightReview, Checkride, IPC,    Aerobatics,   Ground Given,  Tows,   X-C > 50 NM, Legs,   PilotComments
            logBookArray.append([lbDate, lbAcID,     lbFrom, lbTo, lbRoute, '',      '',      '',     '',     '',     '',          lbTotalTime, lbPIC,   lbSIC,  lbNight, lbSolo, lbCrossCountry, '',       lbDayTakeOffs, lbDayLandings,       lbNightLandings, lbNightLandings,       lbDayLandings + lbNightLandings, lbActualInstrument, lbSimInstrument,     '',         '',       '',        '',      '',    '',           '',           '',           '',           '',           '',           lbDualGiven, lbDualReceived, '',              lbGroundReceived, '',             '',                 '',           '',           '',           '',           '',           '',           '',           '',        '',     lbAerobatics, lbGroundGiven, lbTows, lbXC50NM,    lbLegs, lbPilotComments])
    except Exception as Ex:
        print("Error: " + str(Ex))
        
        
if __name__ == '__main__':
   
    lbpLogbookFile = GetLatestCSVFile()
    ImportLogBookCSV(lbpLogbookFile)
    ImportAircraftTXT(lbpAircraftFile)
    CreateAircraftList()
    CreateLogBookList()
    AssembleTemplateData()
    print('Complete!')
