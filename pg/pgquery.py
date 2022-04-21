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
from queries import Queries

class PGQuery:
    key = None
    project = None
    pgconn = None
    lbind_vars = None
    qry = None
    
    def __init__(self, pgconn, qry, lbind_vars = None, query_extension = None):
        if pgconn is None:
            raise Exception("Cannot instantiate PGQuery, None pgconn passed")
        self.pgconn = pgconn
        self.qry = qry
        self.lbind_vars = lbind_vars
        if self.pgconn is None:
            Exception("None PGQuery passed, irrelevant connection context!")
        if qry is None:
            Exception("Query string is none, did you pass a query string!")
    
    # # Adds additional parameters to query (if any) and then executes it.
    # def get_issues_for_query(self, issue_types: List, created_date, **kwargs):

    #     issue_types_str = ', '.join("\'" + t + "\'"  for t in issue_types)
    #     self.qry = self.qry + " AND ISSUE_TYPE IN ( $issue_types )"
    #     self.qry = self.qry + " AND CREATED_ON > '$created_date' "
    #     self.qry = Template(self.qry).substitute({'issue_types': issue_types_str, 'created_date': created_date})

    #     # Processing special parameters like max_rows
    #     params = {}
    #     for key, value in kwargs.items():
    #         params[key] = value

    #     max_rows = 0
    #     if "max_rows" not in params.keys():
    #         max_rows = 25000 # the default
    #     else:
    #         max_rows = params["max_rows"] # The max rows which is provided


    #     if params.get("query", None) is not None:
    #         print("PGSolution.get_issues_for_query() adding %s to query string"% params["query"])
    #         self.qry = self.qry + " AND " + params["query"]
        
    #     # Set the LIMIT Here
    #     self.qry = self.qry + " LIMIT  " + str(max_rows)
    #     # LIMIT setting ending 

    #     print("Executing \"" + self.qry + "\" calling search_issues")
    #     results = list()
    #     try:
    #         results = self.search_issues()
    #     except psycopg2.DatabaseError as dbe:
    #         print("Caught error %s" % (dbe.pgerror))
    #         raise
    #     except psycopg2.ProgrammingError as dbe:
    #         print("Caught error %s" % (dbe.pgerror))
    #         raise
    #     except Exception as e:
    #         print("Exception %s" % (e))
    #         exit(1)
    #     print("Returning %d rows" % (len(results)))
    #     return results

    def search_issues(self) -> List:
        print("PGQuery.search_issues() - Query is %s" % (self.qry))
        try:
            cur = self.pgconn.cursor()
            cur.execute(self.qry)
            results = cur.fetchall()
            cur.close()
        except psycopg2.ProgrammingError as pge:
            print("search_issues(): Database exception - %s" % (pge.pgerror))
            raise
        except Exception as e:
            print("PGSolution.search_issues(): Exception - %s" % (e))
        return results
