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
