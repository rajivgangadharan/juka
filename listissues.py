#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  listissues.py
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

from utils import RunParams, JiraConn, DeferredEpics, ConfigFile, Issue
from project import Project
import sys
import argparse 

def main():
    username = password = server = None
    cfg = None
    try:
        cf = ConfigFile('config.yaml')
        cfg = cf.config
        username = cfg['username']
        password = cfg['password'] 
        server = cfg['server']
    except FileNotFoundError as e:
        print("Config File does not exist." + e.strerror)
        exit(1)
    parser = argparse.ArgumentParser(prog='listissues', description="Will list issues from jira")
    parser.add_argument('--project', help="Provide Project Name", required=True)
    parser.add_argument('--output', help="Output file")
    parser.add_argument("--query", help='Query string to filter your fetch')
    args = parser.parse_args()
    project_string = args.project
    output_file = args.output
    query_string = args.query
    if (project_string is None):
        parser.print_help()
        raise Exception("Project is None, check command line")
    
    if (output_file is not None):
        try:
            of = open(output_file, "w")
        except OSError as oe:
            print("Error while opening file for writing - errno {} message {}",
                oe.errno, oe.strerror)
            sys.exit(oe.errno)
    
    # Connect to jira
    jc = JiraConn(username, password, server)
    assert(jc != None) 
    p = Project(jc.jira, project_string)
    issues = p.get_issues_for_query(max_rows=50, query=query_string)
    for i in issues:
        issue = Issue(jc.jira, i.key)
        print(issue.i.key, issue.i.fields.issuetype, 
            issue.i.fields.status, issue.i.fields.priority,
            issue.i.fields.created, issue.i.fields.updated, 
            issue.i.fields.customfield_13000, sep='|')
        if (output_file is not None):
            print(issue.i.key, issue.i.fields.issuetype,
                  issue.i.fields.status, issue.i.fields.priority,
                  issue.i.fields.created, issue.i.fields.updated,
                  issue.i.fields.customfield_13000, sep='|', file=of)

if __name__ == '__main__':
    main()



