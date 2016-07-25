# deviceDetailsScraper
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.0-orange.svg?style=flat-square)
![Requests](https://img.shields.io/badge/Requests-2.10.0-yellow.svg?style=flat-square)

## _Purpose_ 
This is my first attempt at building data mining software. The purpose of this project is to find patterns and make device recommendations to customers from the VMware hardware compatibility lists.

## _Current Status_
This project is still in the testing and development stage. Currently the "deviceDetailsScraper.getDeviceDetails()" function requires the "vcglink" to be in the form of a string exactly how it appears in the all.json file form the url http://partnerweb.vmware.com/service/vsan/all.json . Once called with vcglink string passed as the parameter the fucntion will go to the link and grab all the device details text from inside the html and save them as key value pairs of an Ordered-Dictionary python data structure.

This Data Mining module builds off of my other project found here: 
https://github.com/JordanCWalsh/JSON-comparison-prototype 

### _This prototype is designed to..._
1. download fresh json data from a URL, into an OrderedDict object
2. _if_ an old json fil is present, load stale json data from '.hcl' file 
3. _else if_ old file does not exist, new json will be saved as the old json file (for next comparison run)
4. contrast json data in step 1 to json data in step 2
5 save any changes to csv file
6. save new json over old json 'hcl' file
7. catch a few common errors
8. use parameters set by command-line arguments OR default to variables initialized in the code
9. using my custom module "deviceDetailsScraper" to print VMware device details to csv file

### !!! _PLEASE NOTE_ !!!  
each time you run this script you will OVERWRITE the 'json_old.hcl' file PERMANENTLY, no undo here :)

### _Calling the getDeviceDetails() function_
objective:   HTML scraping function for "VCGlink" url found in each device in the hardware compatibility list found in the 'partnerweb.vmware.com/service/ssd' json list

parameter:   vsgURL = exact string from the dictionary value of the 'vcglink' key that results after parsing each device's json object into OrdedDict dictionaries

returns:   device_details_OD = OrderedDict dictionary data structure with device details headers as Keys, and device details data as Values

## _Command Line Arguments_
### _Calling the script with Required args_
```
$ python JSON_comparison_prototype.py --saveLocation "C:\\foobar\\Filepath\\yourSrc" -urlAddress "http://partnerweb.vmware.com/service/vsan/..."
```
### _Required args explained_
```python
#Required
'-s', '--saveLocation'     #type string, goes first in command line call
'-u', '--urlAddress'       #type string, goes second in command line call
```

## _Future Features_
1. Print device details for HDD list of devices
2. Print device details for CONTROLLER list of devices
3. OPTIMIZE the run time of this script (currently ~7 mins to print complete SSD csv file)
4. Add in OPTIONAL output to generate tweet (i.e. populated tweet after user signs in, learn Twitter API)
5. look for deeper changes in comparison (i.e. anything changed inside each object's nested dictionaries)
6. ...please send me your ideas...

## _Changelog_

- v Beta-1-0-0: Initial commit for development testing and user feedback

## _Author_
Jordan C Walsh

- Github:  <https://github.com/jordancwalsh>
- Linkedin:  <http://www.linkedin.com/in/jordancwalshsoftwaredeveloper>
- Twitter:   <https://twitter.com/jcwsoftwaredev>
