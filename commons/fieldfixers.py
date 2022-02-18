#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  fieldfixers.py
#
#  Copyright 2022 Rajiv Gangadharan <rajiv.gangadharan@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
# Module commons.fieldfixers to fix fields using regex. 
# Rajiv Gangadharan (Feb.2022)

from ast import Str
import re
from typing import List, Any, Union


def fix_categories(test_str: str) -> List[str]:
    glist = list()
    regex = r"value=\'([A-Za-z ]*)\',"

    try:
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            print("Match {matchNum} was found at {start}-{end}: {match}".
                  format(matchNum=matchNum, start=match.start(),
                         end=match.end(), match=match.group()))
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                glist.append(match.group(groupNum))
                print("Group {groupNum} found at {start}-{end}: {group}".
                      format(groupNum=groupNum, start=match.start(groupNum),
                             end=match.end(groupNum), group=match.group(groupNum)))
    except Exception as e:
        print(f"Exception caught while regex operations, {str(e)}")
        raise

    return glist


def strip_numerical_from_severity(test_str) -> Str:
    regex = r"[0-9] - "
    #test_str = "3 - Medium"

    subst = ""
    result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
    return result # Returns the severity with the number and hypen stripped