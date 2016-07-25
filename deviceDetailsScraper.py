'''
Created on Jul 11, 2016

@author: Jordan C Walsh
'''

# imports
import requests, lxml
from bs4 import BeautifulSoup
from collections import OrderedDict
#from datetime import datetime
#from urllib.error import URLError

#model details webspage
#VCG_url = 'http://www.vmware.com//resources//compatibility//detail.php?deviceCategory=ssd&productid=36697'
#output filepath (windows specific)
#VCG_output_path = 'C:\\Users\\jrdnc\\workspace\\testingPrototypes_2016_summerInternship\\'+'VCG_output.txt'
#calendar time-stamp
#formatedTimestamp = datetime.utcfromtimestamp(time.time())

#print data returned from VCGlink to text file
### vcgOutputFile = open(VCG_output_path, 'w')

'''
function: getDeviceDetails()

objective: HTML scraping function for "VCGlink" url found in each device in the hardware compatibility list found
            in the 'partnerweb.vmware.com/service/ssd' json list

parameter: vsgURL = exact string from the dictionary value of the 'vcglink' key that results after parsing each
                    device's json object into OrdedDict dictionaries

returns: device_details_OD = OrderedDict dictionary data structure with device details headers as Keys, and 
                             device details data as Values

@author: Jordan C Walsh
'''
def getDeviceDetails(vcgURL):

    #print data returned from VCGlink to text file
    #vcgOutputFile = open(VCG_output_path, 'w')
    
    ## pull down and print url response using requests library
    urlGETrequest = requests.get(vcgURL)
    
    ## BeautifulSoup to grab html from the given vcg-link, using lxml as parser for html
    soup = BeautifulSoup(urlGETrequest.content, "lxml")
    
    ## initialize list variables for soup parsing
    device_details_headers_text = []
    device_details_data_text = []
    
    ## zoom into the html table we need, and grab the th (table_header) html element
    device_details_headers_HTML = soup.find("table", "details_table_tab1").findAll('th')
    for t in device_details_headers_HTML:
        device_details_headers_text.append(t.text)  ## pull the text out of each <th> element and append it
    
    ## zoom into the html table we need, and grab the <td> (table_data) html element
    device_details_data_HTML = soup.find("table", "details_table_tab1").findAll('td')
    for d in device_details_data_HTML:
        device_details_data_text.append(d.text)  ## pull the text out of each <td> element and append it
    
    #### DELETE, FOR TESTING ONLY ####
    if( len(device_details_headers_text) == len(device_details_data_text) ):
        print("successful retrieval")
    #### DELETE, FOR TESTING ONLY ####
    
    device_details_OD = OrderedDict(zip(device_details_headers_text, device_details_data_text))
    
    #vcgOutputFile.write(str(sys.version)+'\n')
    #vcgOutputFile.write(str(device_details_OD))
    
    #close output file
    #vcgOutputFile.close()
    
    #release memory not in use
    del device_details_headers_text
    del device_details_data_text
    del device_details_headers_HTML
    del device_details_data_HTML
    
    #return OrderedDict with device details headers as Keys, and device details data as Values
    return device_details_OD
    