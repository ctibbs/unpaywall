##Script to check the OA status of a list of DOIs in the Unpaywall database
##
##Usage: >python unpaywall_oa_status.py <DOI_file>
##
##Usage (interactive): >python -i unpaywall_oa_status.py <DOI_file>
##
##Name of <DOI_file> is expected in format: DOIs_YYYYMMDD.csv
##
##Written by C. Tibbs (July 2019)
##Updated by C. Tibbs (Dec 2020)
##Updated by C. Tibbs (Feb 2023)
##

##Import Python packages
import matplotlib.pyplot as plt
import requests
import json
import fileinput
import sys
import re
from http import HTTPStatus
from pathlib import Path
import py_local_settings


##Extract date from filename containing DOIs
try:
    date = re.search('DOIs_(.+?).csv', sys.argv[1]).group(1)
except AttributeError:
    date = ''
outfile = 'OA_Unpaywall_'+date

##Define new variables
count_dois = 0
open_dois = []
closed_dois = []
bad_dois = []
oa_status = []

##Loop over all of the DOIs
for doi_i in fileinput.input():
  
    ##Count number of DOIs
    count_dois += 1

    ##Trim the DOI string
    doi_str = doi_i.strip()
 
    print('')
    print('#'*50)
    print('Checking', doi_str)
    
    ##Call the Unpaywall API
    url = 'https://api.unpaywall.org/v2/'+doi_str
    params = {'email': py_local_settings.UoE_Email}
    r = requests.get(url, params=params)

    ##Check if API call was unsuccessful
    if r.status_code != HTTPStatus.OK:
        print('Problem with this DOI entry in Unpaywall...')
        bad_dois = bad_dois + [doi_str]
        continue

    ##Check if API call was successful
    elif r.status_code == HTTPStatus.OK:
	##Convert data to a dictionary
        data = json.loads(r.text)

        ##Determine OA status
        if data['is_oa'] == True:
            open_dois = open_dois + [doi_str]
            oa_status = oa_status + [data['oa_status']]
        elif data['is_oa'] == False:
            closed_dois = closed_dois + [doi_str]

##Calculate number/percentage of OA items
print('')
print('#'*50)
print('')
print('Number of DOIs checked = ', count_dois)
print('Number of bad DOIs = ', len(bad_dois))
print('Number of closed DOIs = ', len(closed_dois), \
      '(',len(closed_dois)/(len(open_dois)+len(closed_dois))*100.0, '% )')
print('Number of open DOIs = ', len(open_dois), \
      '(',len(open_dois)/(len(open_dois)+len(closed_dois))*100.0, '% )')
print('Number of Gold OA DOIs = ', oa_status.count('gold'), \
      '(', oa_status.count('gold')/(len(open_dois)+len(closed_dois))*100.0, '% )')
print('Number of Green OA DOIs = ', oa_status.count('green'), \
      '(', oa_status.count('green')/(len(open_dois)+len(closed_dois))*100.0, '% )')
print('Number of Bronze OA DOIs = ', oa_status.count('bronze'), \
      '(', oa_status.count('bronze')/(len(open_dois)+len(closed_dois))*100.0, '% )')
print('Number of Hybrid OA DOIs = ', oa_status.count('hybrid'), \
      '(', oa_status.count('hybrid')/(len(open_dois)+len(closed_dois))*100.0, '% )')

##Plot OA fractions
fig = plt.figure()

plt.pie([oa_status.count('gold'), oa_status.count('green'), oa_status.count('bronze'), \
         oa_status.count('hybrid'), len(closed_dois)], labels=['Gold', 'Green', 'Bronze', 'Hybrid', 'Closed'], \
        autopct = '%1.1f%%', colors=['gold', 'green', 'orange', 'gray', 'red'])
plt.title(date+' [N='+str(len(open_dois)+len(closed_dois))+']')
plt.savefig(outfile)


