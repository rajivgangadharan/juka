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

from ast import Str
from typing import List
from venv import create
import yaml
import psycopg2
from string import Template
from pgquery import PGQuery
from queries import Queries

class PGProject:
    project = None
    pgconn = None
    issue_types = None
    query_template = None
    query = None
    pgquery = None

    def __init__(self, pgconn, projects):
        if pgconn is None:
            raise Exception("Cannot instantiate PGProject, None pgconn passed")

        if type(projects) == str:
            self.projects = [projects]
        else:
            self.projects = projects

        self.pgconn = pgconn
        self.query_template = Queries.query_template
        projects_str = ', '.join( "\'" + p + "\'" for p in self.projects)
        self.query = Template(self.query_template).substitute({'projects': projects_str})
  
    # Adds additional parameters to query (if any) and then executes it.
    def get_issues_for_query(self, issue_types: List, created_date, **kwargs):

        issue_types_str = ', '.join("\'" + t + "\'"  for t in issue_types)
        qry = self.query + " AND ISSUE_TYPE IN ( $issue_types )"
        qry = qry + " AND CREATED_ON > '$created_date' "
        qry = Template(qry).substitute({'issue_types': issue_types_str, 'created_date': created_date})

        # Processing special parameters like max_rows
        params = {}
        for key, value in kwargs.items():
            params[key] = value

        max_rows = 0
        if "max_rows" not in params.keys():
            max_rows = 25000 # the default
        else:
            max_rows = params["max_rows"] # The max rows which is provided


        if params.get("query", None) is not None:
            print("PGSolution.get_issues_for_query() adding %s to query string"% params["query"])
            qry = qry + " AND " + params["query"]
        
        # Set the LIMIT Here
        qry = qry + " LIMIT  " + str(max_rows)
        # LIMIT setting ending 

        print("Executing \"" + qry + "\" calling search_issues")
        results = list()
        try:
            pgqry = PGQuery(self.pgconn, qry = qry)
            results = pgqry.search_issues()
        except psycopg2.DatabaseError as dbe:
            print("Caught error %s" % (dbe.pgerror))
            raise
        except psycopg2.ProgrammingError as dbe:
            print("Caught error %s" % (dbe.pgerror))
            raise
        except Exception as e:
            print("Exception %s" % (e))
            exit(1)
        print("Returning %d rows" % (len(results)))
        return results

   