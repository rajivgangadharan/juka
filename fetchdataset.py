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
import sys, yaml,  logging
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

    parser = argparse.ArgumentParser(prog='fetchdataset',
            description="Assembling a dataset for delivery insights")
    parser.add_argument("--batch-size", help='Batch size for Jira fetch', required=False, default=25)
    parser.add_argument("--max-rows", help='Arrest the number of rows processed', required=False, default=1000)
    parser.add_argument("--run_config", help='Config file for run configuration, \
            defaults to fetchdataset.yaml', required=False, default="fetchdataset.yaml")
    args = parser.parse_args()
    max_rows = int(args.max_rows)
    batch_size = int(args.batch_size)
    run_config_file = args.run_config

    # Connect to jira
    jc = JiraConn(username, password, server)
    assert(jc != None)
    ######################################################################
    try:
        print("YAML configurator not provided,  defaulting to fetchdataset.yaml.")
        with open(run_config_file, 'r') as file:
            dsconfig = yaml.safe_load(file)
    except FileNotFoundError as e:
        print("Error, yaml configurator absent, does file exist?")
        exit(200)
    except Exception as e:
        print("Exception occured " + e)
        exit(201)

    for project in dsconfig:
        if (project is None):
            raise Exception("Project is None, check yaml file")
        p = Project(jc.jira, project)
        for query in dsconfig[project].keys():
            created = dsconfig[project][query]['created']
            types = dsconfig[project][query]['issuetypes']
            output_file = dsconfig[project][query]['outputfile']
            issuetypes = ', '.join(types)
            querystr = 'Type in (' + issuetypes + ') AND createdDate >= ' +\
                "\"" + created + "\""
            print("Executing " + querystr + " for " + project)
            issues = p.get_issues_for_query(max_rows=max_rows,
                query=querystr,
                block_size=batch_size)
            print("Collected # " + str(len(issues)) + " issues.")

            # Check if output file can be successfully opened
            # Opening output file
            if (output_file is not None):
                    try:
                        of = open(output_file, "w")
                    except OSError as oe:
                        print("Error openign file - errno {} message {}",  oe.errno, oe.strerror)
                        of.close()
                        sys.exit(oe.errno)

            # Write the header
            header = [
                    "Key",
                    "Type",
                    "Status",
                    "Priority",
                    "Created",
                    "Updated",
                    "Closed"
                ]
            print(*header, sep='\t', file=of)
            for i in issues:
                print(i.key,
                        i.fields.issuetype,
                        i.fields.status,
                        i.fields.priority,
                        i.fields.created,
                        i.fields.updated,
                        i.fields.customfield_13000, sep="\t", file=of)

            if (output_file is not None):
                of.close()
                print("Wrote data file ", output_file)
        ######################################################################
if __name__ == '__main__':
    main()
