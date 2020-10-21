#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  project.py
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

from jira.exceptions import JIRAError
from jira.resilientsession import raise_on_error
from jira.resilientsession import ResilientSession
from jira import JIRA

class Project:
    key = None
    project = None
    jira = None

    def __init__(self, jira, project_string):
        try:
            self.key = project_string
            self.project = jira.project(project_string)
            self.jira = jira
        except JIRAError as e:
            print("Error getting issues list -", e.status_code, e.text)
            raise

    def get_all_issues(self):
        jql_str = "project = " + self.key 
        issues = self.jira.search_issues(jql_str) 
        """ This will return on 50 issues by default
            not modifying it because will never be used """
        return issues

    def get_issues_for_query(self, **kwargs):
        """
        max_rows=50 (default)
        query = pass the query you want here, exclude the project key 
        """
        params = {}
        for key, value in kwargs.items():
            params[key] = value

        if params.get("query", None) is not None:
            jql_str = "project = " + self.key + " and " + params["query"]
        else:
            jql_str = "project = " + self.key
        try:
            result = self.jira.search_issues(jql_str, maxResults=params['max_rows'])
        except JIRAError as e:
            print("Caught error {} {}".format(e.status_code, e.text))
            raise
        return result

    def get_epics_for_planned_iteration(self, iteration_string):
        jql_str = "project = " + self.key +\
            "and cf[14401] = " + iteration_string +\
            "and Type = Epic"
        try:
            epics_for_planned_iteration = self.jira.search_issues(jql_str)
        except JIRAError as e:
            print("Caught error {} {}".format(e.status_code, e.text))
            raise
        return epics_for_planned_iteration
