#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  pgproject.py
#
#  Copyright 2017 Rajiv Gangadharan <rajiv.gangadharan@gmail.com>
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
# Module Jira Utilities for Maintaining Data. Rajiv Gangadharan (Sep.2017)

import yaml
import psycopg2
from string import Template
from typing import List

class Queries:
    query_template = """SELECT 
        JIRA_ISSUE_KEY, 
        ISSUE_TYPE, 
        ISSUE_STATUS,
        PRIORITY, 
        CREATED_ON, 
        UPDATED_DATE, 
        CLOSED_DATE, 
        DEFECT_ORIGIN 
    FROM
        PUBLIC.REPORT_ALL WHERE 
    PROJECT_NAME in ( $projects )"""