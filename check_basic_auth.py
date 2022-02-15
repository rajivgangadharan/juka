#!/home/rajivg/Tools/anaconda3/bin/python3
import re
import sys
 
from jira.jirashell import get_config, JIRA
import requests
 
options = {'server': 'https://jira.finastra.com'}
jira = JIRA(options, basic_auth=('<<username>>', '<<api-key>>'), validate=True)

print(jira)
