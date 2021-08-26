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

class PGProject:
    key = None
    project = None
    pgconn = None

    def __init__(self, pgconn, project_string):
        if pgconn is None:
            raise Exception("Cannot instantiate PGProject, None pgconn passed")
        self.key = project_string
        self.project = project_string
        self.pgconn = pgconn
        if self.pgconn is None:
            Exception("None PGConn passed, irrelevant connection context!")

    def search_issues(self, qry):
        try:
            cur = self.pgconn.cursor()
            cur.execute(qry)
            results = cur.fetchall()
            cur.close()
        except psycopg2.ProgrammingError as pge:
            print("search_issues(): Exception - %s" % (pge.pgerror))
            raise
        return results

    def get_all_issues(self):
        sql_str = "project_name = " + self.key
        try:
            issues = self.search_issues(sql_str)
        except Exception as e:
            print("get_all_issues(): Exception - %s" % (e))
            raise
        return issues

    def get_issues_for_query(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            params[key] = value

        max_rows = 0
        if "max_rows" not in params.keys():
            max_rows = 5000 # the default
        else:
            max_rows = params["max_rows"] # The max rows which is provided

        if params.get("query", None) is not None:
            sql_str = 'SELECT JIRA_ISSUE_KEY, ISSUE_TYPE, ISSUE_STATUS,\
            PRIORITY, CREATED_ON, UPDATED_DATE, CLOSED_DATE FROM \
            PUBLIC.REPORT_ALL WHERE '+ "project_name = " + "'" + \
            self.key + "'" + " AND " + params["query"]
        else:
            sql_str = 'SELECT JIRA_ISSUE_KEY, ISSUE_TYPE, ISSUE_STATUS,\
            PRIORITY, CREATED_ON, UPDATED_DATE, CLOSED_DATE FROM \
            PUBLIC.REPORT_ALL WHERE '+ "project_name = " + self.key

        print("Executing \"" + sql_str + "\"")
        results = list()
        try:
            results = self.search_issues(sql_str)
        except psycopg2.DatabaseError as dbe:
            print("Caught error %s" % (dbe.pgerror))
            raise
        except psycopg2.ProgrammingError as dbe:
            print("Caught error %s" % (dbe.pgerror))
            raise
        except Exception as e:
            print("Exception %s" % e)
            exit(1)
        print("Returning %d rows" % (len(results)))
        return results
