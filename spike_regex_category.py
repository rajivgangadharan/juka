#!/usr/bin/env python
# coding=utf8
# Spike for regular expression to extract category from the category field of JIRA.
# The function will be incorporated into fetchdataset.py in the final commit.

import re
from typing import List, Any, Union

def get_categories(test_str:str) -> List[str]:
    glist = list()
    regex = r"value=\'([A-Za-z ]*)\',"
    matches = re.finditer(regex, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        print("Match {matchNum} was found at {start}-{end}: {match}".
                format(matchNum = matchNum, start = match.start(), 
                    end = match.end(), match = match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            glist.append(match.group(groupNum))
            print ("Group {groupNum} found at {start}-{end}: {group}".
                    format(groupNum = groupNum, start = match.start(groupNum), 
                        end = match.end(groupNum), group = match.group(groupNum)))
    return glist

def main():
    test_str = "[<JIRA CustomFieldOption: value='Opics Capital Markets', id='23604'>]"
    gl = get_categories(test_str)
    print(gl[0])

if __name__ == '__main__':
    main()
