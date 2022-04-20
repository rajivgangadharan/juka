#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pgfetchsolutiondatasets.py
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
from pprint import pprint
import sys
from pgutils import PGConfigFile,PGConn
from pgsolution import PGSolution
from pgproject import PGProject
import sys,yaml,logging
import argparse
import psycopg2
from string import Template

def main():
    parser = argparse.ArgumentParser(prog='pgfetchsolutiondatasets',
     description="Assembling a dataset from Postgres Reporting Database for delivery insights")
    parser.add_argument("--auth-config", help="YAML file with database connection parameters", default='pgconfig.yaml', required=False)
    parser.add_argument("--max-rows", help='Arrest the number of rows processed', required=False, default=25000)
    parser.add_argument("--config", help='Config file (default: datafetch.yaml)', required=False, default="datafetch.yaml")
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
        print("YAML configurator not provided,  defaulting to solutionfetch.yaml.")
        with open(run_config_file, 'r') as file:
            dsconfig = yaml.safe_load(file)
            print(dsconfig)
    except FileNotFoundError as e:
        print(f'Error, yaml configurator absent, does file exist? {e}')
        exit(200)
    except Exception as e:
        print("Exception occured. ", e)
        exit(201)

    for level in dsconfig.keys():
        print(f"Processing level {level}")
        logging.info("####### " + level + " ########")
        if level == 'projects':
            for project in dsconfig[level].keys():
                print(f"Processing project {project}")
                if (project is None):
                    raise Exception("Project is None, check yaml file")
                p = PGProject(pgconn, project)
                for query in dsconfig[level][project].keys():
                    created = dsconfig[level][project][query]['created']
                    types = dsconfig[level][project][query]['issuetypes']
                    output_file = dsconfig[level][project][query]['outputfile']
                    issues = p.get_issues_for_query(types, created, max_rows=max_rows)
                    logging.info("Collected # " + str(len(issues)) + " issues.")

                    # Check if output file can be successfully opened
                    # Opening output file
                    if (output_file is not None):
                        try:
                            of = open(output_file, "w")
                        except OSError as oe:
                            print(f"Error opening file - errno {oe.errorno} message {oe.strerror}")
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
                        print(f"Wrote data file {output_file}")
                        logging.info("Wrote data file ", output_file)


        if level == 'solutions':
            for solution in dsconfig[level].keys():
                if (solution is None):
                    raise Exception("Project is None, check yaml file")
                projects = dsconfig[level][solution]['projects']
                print(f"Solution being processed is {solution} with ")  
                pprint(projects)
                s = PGSolution(pgconn, solution, projects=projects)    

                for query in dsconfig[level][solution]['queries'].keys():
                    print(f"Query being processed is {query}")
                    created = dsconfig[level][solution]['queries'][query]['created']         
                    types = dsconfig[level][solution]['queries'][query]['issuetypes']
                    output_file = dsconfig[level][solution]['queries'][query]['outputfile']
                    print(f"From created date {created} with {types} writing to {output_file}")

                    issues = s.get_issues_for_query( \
                        issue_types=types, created_date=created, max_rows=max_rows)
                    logging.info("Collected # " + str(len(issues)) + " issues.")

                    # Check if output file can be successfully opened
                    # Opening output file
                    if (output_file is not None):
                        try:
                            of = open(output_file, "w")
                        except OSError as oe:
                            print(f"Error opening file - errno {oe.errorno} message {oe.strerror}")
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
                        print(f"Wrote data file {output_file}")
                        logging.info("Wrote data file ", output_file)
if __name__ == '__main__':
    main()
