#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pgfetchdataset.py
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
import sys
from pgutils import PGConfigFile,PGConn
from pgproject import PGProject
import sys,yaml,logging
import argparse
import psycopg2
from string import Template

def main():
    parser = argparse.ArgumentParser(prog='pgfetchdataset',
     description="Assembling a dataset from Postgres Reporting Database for delivery insights")
    parser.add_argument("--auth-config", help="YAML file with database connection parameters", default='pgconfig.yaml', required=False)
    parser.add_argument("--max-rows", help='Arrest the number of rows processed', required=False, default=1000)
    parser.add_argument("--config", help='Config file (default: project.yaml)', required=False, default="projectfetch.yaml")
    parser.add_argument("--log-level", help="Set your log level.", required=False, default="CRITICAL")
    args = parser.parse_args()
    max_rows = int(args.max_rows)
    run_config_file = args.config
    loglevel = args.log_level
    auth_config = args.auth_config
    username = password = server = None
    cfg = None
    try:
        cf = PGConfigFile(auth_config)
        cfg = cf.config
        username = cfg['username']
        password = cfg['password']
        server = cfg['server']
        port = cfg['port']
        database = cfg['database']
    except FileNotFoundError as e:
        logging.error("Config File does not exist." + e.strerror)
        exit(1)

    numeric_log_level = getattr(logging, loglevel.upper())
    if (not isinstance(numeric_log_level, int)):
        raise ValueError("Invalid numeric_log_level : %s" % numeric_log_level)
    logging.basicConfig(filename="pgfetchdataset.log",
                        level=numeric_log_level,
                        filemode='a',
                        format="%(asctime)s %(message)s",
                        datefmt="%Y:%m:%d %H:%M:%S")


    # Connect to jira
    pg = PGConn(username, password, server, port, database)
    pgconn = pg.pgconn
    assert(pgconn != None)

    try:
        print("YAML configurator not provided,  defaulting to pgfetchdataset.yaml.")
        with open(run_config_file, 'r') as file:
            dsconfig = yaml.safe_load(file)
            print(dsconfig)
    except FileNotFoundError as e:
        print(f'Error, yaml configurator absent, does file exist? {e}')
        exit(200)
    except Exception as e:
        print("Exception occured. ", e)
        exit(201)

    for project in dsconfig:
        if (project is None):
            raise Exception("Project is None, check yaml file")
        p = PGProject(pgconn, project)
        for query in dsconfig[project].keys():
            created = dsconfig[project][query]['created']
            types = dsconfig[project][query]['issuetypes']
            output_file = dsconfig[project][query]['outputfile']
            issuetypes = ', '.join("\'" + t + "\'"  for t in types)
            query_templ_str = """ISSUE_TYPE in (
            $issue_types
            ) AND created_on >= $created_date"""
            query_templ = Template(query_templ_str)
            created_str = '\'' + str(created) + '\''
            querystr = query_templ.substitute({'issue_types': issuetypes,
            'created_date': created_str})
            issues = p.get_issues_for_query(max_rows=max_rows, query=querystr)
            logging.info("Collected # " + str(len(issues)) + " issues.")

            # Check if output file can be successfully opened
            # Opening output file
            if (output_file is not None):
                    try:
                        of = open(output_file, "w")
                    except OSError as oe:
                        print("Error opening file - errno {} message {}",  oe.errno, oe.strerror)
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
                    "Closed",
                    "Origin"
                ]
            print(*header, sep='\t', file=of)
            for i in issues:
                print(*i, sep="\t", file=of)
            if (output_file is not None):
                of.close()
                logging.info("Wrote data file ", output_file)
if __name__ == '__main__':
    main()
