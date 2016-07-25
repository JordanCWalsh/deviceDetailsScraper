'''
Started on May 24, 2016
@author: Jordan C Walsh
project repo:  https://github.com/JordanCWalsh/JSON-comparison-prototype

This prototype is designed to:
    1. download fresh json data from a URL, into an OrderedDict object
    2. _if_ an old json fil is present, load stale json data from '.hcl' file 
    3. _else if_ old file does not exist, new json will be saved as the old json file (for next comparison run)
    4. contrast json data in step 1 to json data in step 2
    5 save any changes to csv file
    6. save new json over old json 'hcl' file
    7. catch a few common errors
    8. use parameters set by command-line arguments OR default to variables initialized in the code
NEW_9. using custom module "deviceDetailsScraper" to print VMware device details to csv file

...my file-nameing convention (MUST name files this way)
...STALE json file = 'json_old.hcl'   
----------------------------------
!!! _PLEASE NOTE_ !!!  
each time you run this script you
will OVERWRITE the 'json_old.hcl'
file PERMANENTLY, no undo here :)
For you own records you can save
the 'json_old.hcl' as a new name.
----------------------------------

FUTURE FEATURES:
i)     Print device details for HDD list of devices
ii)    Print device details for CONTROLLER list of devices
iii)   OPTIMIZE the run time of this script (currently ~7 mins to print complete SSD csv file)
iv)    Add in OPTIONAL output to generate tweet (i.e. populated tweet after user signs in, learn Twitter API)
v)     look for deeper changes in comparison (i.e. anything changed inside each object's nested dictionaries)
'''

# imports
import os, sys, time, glob, json, urllib.request, copy, csv, argparse
from collections import OrderedDict
from datetime import datetime
from deepdiff import DeepDiff
from urllib.error import URLError
import deviceDetailsScraper


#-- argparse function for command line --#
def get_args():
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Script prints multiple csv reports for the VMware hardware compatibility list')
    parser.add_argument(
        '-s', '--saveLocation', type=str, help='do not include file name, this is the python _C:\\.._ file path for all files needed and created', required=True)
    parser.add_argument(
        '-u', '--urlAddress', type=str, help='UrlAddress of all.json', required=True)
    # Array for all arguments passed to script
    args = parser.parse_args()
    # Assign args to variables
    allFilesLocation = args.saveLocation
    updatesUrl = args.urlAddress
    # Return all variable values
    return allFilesLocation, updatesUrl

try:
    # match argparse return values to variables
    #NOTE! program crashes if no arguments are used in the args
    allFilesPath, url = get_args()
    
    
    # strings we need from our JSON object to be searched
    PARENT_KEY = "data"
    CHILD_KEY_0 = "controller"
    CHILD_KEY_1 = "hdd"
    CHILD_KEY_2 = "ssd"
    TARGET_KEY_A = "id"         # target keys should be present in all objects of the 'child_key_# : value-array'
    TARGET_KEY_vcglink = "vcglink"
    
    # file names for saving stuff
    oldjsonfilename = 'json_old.hcl'
    comparisonCsvFilename = 'JSON_comparison_Output_Beta_1.0.3.csv'
    detailedSSDcsvFilename = 'Data_Mining_Output_SSD_Beta_1.0.1.csv'
    logFilename = 'logs.txt'
    
    # count of child keys for loops
    CHILD_LIST = [CHILD_KEY_0, CHILD_KEY_1, CHILD_KEY_2]
    CHILD_COUNT = len(CHILD_LIST)
    
#     # url string and file path syntax (a Python headache)
#     url = "http://partnerweb.vmware.com/service/vsan/all.json"
    
    # initialize all files paths using the save location from args
    oldpath = allFilesPath+oldjsonfilename
    pathToDIFFcsv = allFilesPath+comparisonCsvFilename
    pathToSSDcsv = allFilesPath+detailedSSDcsvFilename
    logsPath = allFilesPath+logFilename
    
#     # windows specific file paths
#     oldpath = 'C:\\Users\\jrdnc\\workspace\\testingPrototypes_2016_summerInternship\\json_old.hcl'
#     pathToDIFFcsv = 'C:\\Users\\jrdnc\\workspace\\testingPrototypes_2016_summerInternship\\JSON_comparison_Output_Beta_1.0.2.csv'
#     logsPath = 'C:\\Users\\jrdnc\\workspace\\testingPrototypes_2016_summerInternship\\logs.txt'
#     
#     pathToSSDcsv = 'C:\\Users\\jrdnc\\workspace\\testingPrototypes_2016_summerInternship\\Data_Mining_Output_SSD_Beta_1.0.0.csv'
    
    oldjsonfilepath = glob.glob(oldpath)
    
    
    #calendar time-stamp
    formatedTimestamp = datetime.utcfromtimestamp(time.time())
    #print to log
    logFile = open(logsPath, 'w')
    logFile.write(str(sys.version)+'\n')
    logFile.write(str(time.time())+'\n')
    logFile.write("UTC time-stamp = " + str(formatedTimestamp)+'\n' )
    #print to console
    print(sys.version)
    print(time.time())
    print("UTC time-stamp = " + str(formatedTimestamp) )

#===================#
#     VCGlink = 'http://www.vmware.com//resources//compatibility//detail.php?deviceCategory=ssd&productid=36697'
#     SSDid36697_deviceDetailsOD = deviceDetailsScraper.getDeviceDetails(VCGlink)
#     print(str(SSDid36697_deviceDetailsOD))
#===================#

    # download fresh JSON
    urlresponse = urllib.request.urlopen(url).read().decode('UTF-8')
    todaysJSON = json.loads(urlresponse, object_pairs_hook=OrderedDict)

    # check for valid old_hcl file
    if ( os.path.isfile(oldpath) ):
        
        #load old_hcl file into OrderedDict
        with open(oldjsonfilepath[0]) as json_file:
            staleJSON = json.load( json_file, object_pairs_hook=OrderedDict)
    
        #pull all id-VALUES into a list, one for today, second for old    
            todaysIDlist = []           #int arrays for device IDs
            staleIDlist = []
            
            todaysHDDcount  = 0         # device counts for verification
            todaysSSDcount  = 0
            todaysCONTROLLERcount = 0
            
            childArrayIndex = 0     #in all.json.. 0->controller, 1->hdd, 2->ssd
            
        # build todays id list   
            for jsonObject in todaysJSON[PARENT_KEY][CHILD_KEY_0]:
                todaysIDlist.append(jsonObject[TARGET_KEY_A])
                todaysCONTROLLERcount += 1
            
            for jsonObject in todaysJSON[PARENT_KEY][CHILD_KEY_1]:
                todaysIDlist.append(jsonObject[TARGET_KEY_A])
                todaysHDDcount += 1
                
            for jsonObject in todaysJSON[PARENT_KEY][CHILD_KEY_2]:
                todaysIDlist.append(jsonObject[TARGET_KEY_A])
                todaysSSDcount += 1
            
        # build stale id list
            while( childArrayIndex != CHILD_COUNT ):    
                for jsonObject in staleJSON[PARENT_KEY][CHILD_LIST[childArrayIndex]]:
                    staleIDlist.append(jsonObject[TARGET_KEY_A])   
                childArrayIndex += 1
            
        #-- GET NEWLY ADDED ID's IN TODAYS LIST --# 
            todaysIDlist.sort()
            staleIDlist.sort()
            changes = DeepDiff(staleIDlist, todaysIDlist)
            #print(json.dumps(changes, indent=2))
            #logFile.write("DeepDiff changes found:\n"+str(json.dumps(changes, indent=2)))
            
        #-- Exit program if no changes are found --#
            if( len(changes)<1 ):
                logFile.write("sys.exit... no new json data at that url yet, check back later.\n")
                print("no new json data at that url yet, check back later.")
                
                #clear memory not in use
                del todaysIDlist
                del staleIDlist
                del staleJSON
                
        #-- if changes are found continue... --#        
            else:
                listOfNewIDs = copy.deepcopy( list( changes["iterable_item_added"].values() ) )
                listOfNewIDs.sort()
                print(listOfNewIDs)
                logFile.write("list of new IDs found:\n"+str(listOfNewIDs)+"\n")
            
        #close old json file from above
            json_file.close()
        ### END OPEN, closed old_hcl file ###
        
        #--- only print new IDs to CSV if deepDiff module finds changes ---#
        if( len(changes) > 1 ):
            
            #---- print new id's object to a csv file ----#
            childArrayIndex = 0             # reset indices
            count = 0
            allNewValuesList = []           # a list of 'KVpairList' objects to print to csv from
            KVpairList = OrderedDict([])    # temp list of [key,value] objects for each new device printed to csv files
            keysListMaster = []             # master keys list to be headers for all columns in csv files
            keysList = []                   # temp keys list to compare
            
            with open(pathToDIFFcsv, 'w', newline='') as outputfile:
                outputWriter = csv.writer(outputfile)
                
                # initialize keys list to first set of keys 
                keysListMaster = list(todaysJSON[PARENT_KEY][CHILD_LIST[0]][0].keys())
                
                #---- find and record only new objects ----#
                while( childArrayIndex != CHILD_COUNT ):
                    for jsonObject in todaysJSON[PARENT_KEY][CHILD_LIST[childArrayIndex]]:
                        if( jsonObject[TARGET_KEY_A]  in  listOfNewIDs ):
                            
                            #-- save all object data --#
                            KVpairList = OrderedDict(jsonObject.items())
                            
                            #-- save keys to a list to compare to master --#
                            for k,v in jsonObject.items():
                                keysList.append(k)
                            
                            #-- update master key list if new list is longer --#
                            if( len(keysList) > len(keysListMaster) ):
                                del keysListMaster[:]
                                keysListMaster += keysList
                                 
                            #-- add each new values list to an 'allNewValuesList' to print to csv after looping --#
                            allNewValuesList.append(KVpairList.copy())
                            
                            #-- erase values list to reuse in looping statement --#
                            del KVpairList
                            KVpairList = OrderedDict([])
                            del keysList[:]
        
                    childArrayIndex += 1
                    
                #---- print to csv file ----#
                # column headers
                outputWriter.writerow( keysListMaster ) #-- row 1 in csv sheet --#
                
                # values in matching columns
                csvrow = ['n/a']*(len(keysListMaster))  # temp to build each row of csv output according to headers list 
                klmIndex = 0                            # key list master index int for csv print loops
                csvNewRowsCount = 0                     # count of csv rows (other that col headers) printed to check successful printing
                
                #DevNotes# allNewValuesList[current object made of 'k,v' lists [current KV tuple in this list object]]
                for newDevice in allNewValuesList:         #-- rows 2 thru end of csv sheet --#
                    for key in newDevice.keys():
                        header = key
                        value = newDevice[key]
                        if( str(header) in keysListMaster ):        # append values for matching headers
                            klmIndex = keysListMaster.index(str(header))
                            csvrow[klmIndex] = value
                #---- INSERT VSGLINK FUCNTION CALL HERE FOR EACH 'newDevice' in allNewValuesList ----#
                        
                    # now print this device's csvrow to the csv file
                    if(len(csvrow) > 0):
                        outputWriter.writerow(csvrow)
                        csvNewRowsCount += 1
                    else:
                        print("error in adding values to the csvrow list")
                        logFile.write("while printing new csv rows, encouterned following error...\n"+
                                      "error in adding values to the csvrow list before printing \n")
                        
                    del csvrow[:]   # reset csvrow for next device
                    csvrow = ['n/a']*(len(keysListMaster)) # re-populate temp list with 'n/a' strings
                    klmIndex = 0    # reset index for next device
                    
                
                #-- upon csv print success, replace old_json.hcl data with new json from url --#
                print("new device csv rows printed: "+str(csvNewRowsCount))
                print("new device list length: "+str(len(allNewValuesList)))
                logFile.write("new device csv rows printed: "+str(csvNewRowsCount)+"\n")
                logFile.write("new device list length: "+str(len(allNewValuesList))+"\n")
                
                # check for success
                if( csvNewRowsCount == len(allNewValuesList) ):
                    print("these numbers matched, successful csv printed!")
                    logFile.write("these numbers matched, successful csv printed!\n")
                    with open(oldpath, 'w') as replacingOldHCL:
                        json.dump(todaysJSON, replacingOldHCL, ensure_ascii=False)
                        replacingOldHCL.close()
                    print("old json has been overwritten with newest json for next comparison.")
                    logFile.write("old json has been overwritten with newest json for next comparison.\n")
                # print error msg if unsuccessful 
                else:
                    print("these numbers must match for successful printing...")
                    print("there was an error in the 'print to csv file' section of the program.")
                    logFile.write("these numbers must match for successful printing...\n")
                    logFile.write("there was an error in the 'print to csv file' section of the program.\n")
                    
                # close csv file when no longer needed
                outputfile.close()
                
        ####  END of Conditional CSV printing  ####
        
        #clear memory not in use if not previously deleted
        if( len(changes) > 1 ):
            del todaysIDlist
            del staleIDlist
            del staleJSON
        
        '''### 
        regardless of DeepDiff findings, print device data for HDD, SSD and CONTROLLER csv files 
        ###'''
        
        '''SSD csv'''
        #--- Print todays SSD data with Device Details to new CSV file ---#
        count = 0                           # reset count var
        allSSDValuesList = []               # a list of 'KVpairList' objects to print to csv from
        KVpairList = OrderedDict([])        # temp list of [key,value] objects for each new device printed to csv files
        keysListMaster = []                 # master keys list to be headers for all columns in csv files
        keysList = []                       # temp keys list to compare
        deviceDetailsOD = OrderedDict([])   # ordered dictionary temp for printing device details to csv
        vcglinkTemp = ""                    # temp string for vcglinks
        
        # print SSD count for testing
        print("number of SSDs to print: "+str(todaysSSDcount))
        
        with open(pathToSSDcsv, 'w', newline='') as SSDoutput:
            SSDoutputWriter = csv.writer(SSDoutput)
             
            # initialize keys list to first set of SSD device keys 
            keysListMaster = list(todaysJSON[PARENT_KEY][CHILD_KEY_2][0].keys())
            
            ### create master key list for headers and gather json data for all SSDs
            for jsonObject in todaysJSON[PARENT_KEY][CHILD_KEY_2]:
                 
                # save all object data --#
                KVpairList = OrderedDict(jsonObject.items())
                 
                # save keys to a list to compare to master --#
                for k,v in jsonObject.items():
                    keysList.append(k)
                # update master key list if current key list is longer
                if( len(keysList) > len(keysListMaster) ):
                    del keysListMaster[:]
                    keysListMaster += keysList
                    
                # add each SSD device data to an 'allSSDValuesList' to print to csv after looping 
                allSSDValuesList.append(KVpairList.copy())
                
                # erase values list to reuse in looping statement
                del KVpairList
                KVpairList = OrderedDict([])
                del keysList[:]
                
            ###
            
            # delete json data no longer needed
            
            ''' NEW! get device details dictionary of first SSD, use keys as headers '''
            # grab first vcglink from SSD in json      
            for key in allSSDValuesList[0].keys():
                header = key
                if( str(header) == "vcglink"):
                    vcglinkTemp = allSSDValuesList[0][key]
                else:
                    del header
            # check for nonempty string before sending for device details        
            if(len(vcglinkTemp) > 1):
                ''' NEW! scrape vcglink page for device details of first SSD id '''
                deviceDetailsOD = deviceDetailsScraper.getDeviceDetails(vcglinkTemp)
                # get keys from dictionary above, add them to master list
                for keyddOD in deviceDetailsOD.keys():
                    keysListMaster.append(keyddOD)

            else:
                print("error while pulling first vcglink in allSSDValuesList[0].keys() list for loop.\n"+
                      "device details will not be printed to SSD csv.")
            
            #--- build CSV file of SSDs with Device Details ---#
            # write keys as column headers
            SSDoutputWriter.writerow( keysListMaster ) #-- row 1 in SSD csv sheet --#
            
            # values in matching columns
            csvrow = ['n/a']*(len(keysListMaster))  # temp to build each row of csv output according to headers list 
            klmIndex = 0                            # key list master index int for csv print loops
            csvSSDRowsCount = 0                     # count of csv rows (other that col headers) printed to check successful printing

            #DevNotes# allSSDValuesList[current object made of 'k,v' lists [current KV tuple in this list object]]
            for newDevice in allSSDValuesList:         #-- rows 2 thru end of csv sheet --#
                
                # newDevice keys from json device data
                for key in newDevice.keys():
                    header = key
                    value = newDevice[key]
                    
                    # print values to csv in matching headers/columns
                    if( str(header) in keysListMaster ):
                        klmIndex = keysListMaster.index(str(header))
                        csvrow[klmIndex] = value
                        
                    # call getDeviceDetails function for each 'newDevice' in allSSDValuesList
                    if ( str(header) == "vcglink"):
                        vcglinkTemp = newDevice[key]
                        # check for nonempty string before sending for device details        
                        if(len(vcglinkTemp) > 1):
                            # get device details of first SSD id
                            deviceDetailsOD = deviceDetailsScraper.getDeviceDetails(vcglinkTemp)
                
                # newDevice keys from deviceDetailsOD device data
                # NOTE! script crashes here if vcglink could not be reached
                for keyDD in deviceDetailsOD.keys():
                    headerDD = keyDD
                    valueDD = deviceDetailsOD[keyDD]
                    
                    # print values to csv in matching headers/columns
                    if( str(headerDD) in keysListMaster ):
                        klmIndex = keysListMaster.index(str(headerDD))
                        csvrow[klmIndex] = valueDD
                
                # PRINT THIS DEVICE TO CSV ROW
                if(len(csvrow) > 0):
                    SSDoutputWriter.writerow(csvrow)
                    csvSSDRowsCount += 1
                else:
                    print("error in adding values to the SSD csvrow list")
                    logFile.write("while printing SSD csv rows, encouterned following error...\n"+
                                  "error in adding values to the csvrow list before printing \n")
                
                # Clear memory for next loop
                del csvrow[:]   # reset csvrow for next device
                csvrow = ['n/a']*(len(keysListMaster)) # re-populate temp list with 'n/a' strings
                klmIndex = 0    # reset index for next device
                deviceDetailsOD.clear()
                
                
            
            #-- upon csv print success, replace old_json.hcl data with new json from url --#
            print("SSD device csv rows printed: "+str(csvSSDRowsCount))
            
    
    # else for if hcl file is not found  
    # save todays as the 'old_json.hcl' to use as comparison tmrw      
    else:
        print("file >json_old.hcl< does not exist at specified path, nothing to compare")
        print("creating a new hcl file ..\\json_old.hcl.. with new json from the given url")
        logFile.write("file >json_old.hcl< does not exist at specified path, nothing to compare\n")
        logFile.write("creating a new hcl file ..\\json_old.hcl.. with new json from the given url\n")
        
        with open(oldpath, 'w') as newHCLfile:
            json.dump(todaysJSON, newHCLfile, ensure_ascii=False)
        newHCLfile.close()
        
    
# exceptions for common errors
except URLError:
    print(str(URLError) + "... HCL DIFF operation ended. Check URL string for correctness.")
    logFile.write(str(URLError) + "... HCL DIFF operation ended. Check URL string for correctness.\n")
except PermissionError:
    print(str(PermissionError) + "... Make sure csv file is closed, and that you have access to it on your system.")
    logFile.write(str(PermissionError) + "... Make sure csv file is closed, and that you have access to it on your system.\n")
    
#close the log file
logFile.close()

