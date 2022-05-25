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
import sys, os
from pgutils import PGConfigFile,PGConn
from pgsolution import PGSolution
from pgproject import PGProject
from pathlib import Path
import sys,yaml,logging
import argparse
import psycopg2
from string import Template

def main():
    parser = argparse.ArgumentParser(prog='pgfetchsolutiondatasets',
     description="Assembling a dataset from Postgres Reporting Database for delivery insights")
    parser.add_argument("--auth-config", help="YAML file with database connection parameters", \
        default='pgconfig.yaml', required=False)
    parser.add_argument("--max-rows", help='Arrest the number of rows processed', \
        required=False, default=25000)
    parser.add_argument("--config", help='Config file (default: pgfetchdatasets.yaml)', \
        required=False, default="pgfetchdatasets.yaml")
    parser.add_argument("--log-level", help="Set your log level.", required=False, \
        default="INFO")
    parser.add_argument("--log-file", help="Log file name.", required=False, \
        default="pgfetchdatasets.log")
    parser.add_argument("--data-dir", help="Data directory, defaults to home", \
        required=False, default=None)
    args = parser.parse_args()
    max_rows = int(args.max_rows)
    run_config_file = args.config
    log_level = args.log_level
    auth_config = args.auth_config
    data_dir = args.data_dir
    username = password = server = None
    log_file_name = args.log_file
    cfg = None

    numeric_log_level = getattr(logging, log_level.upper())
    if (not isinstance(numeric_log_level, int)):
        raise ValueError("Invalid numeric_log_level : %s" % numeric_log_level)

    log_format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = logging.getLogger('pgfetchdatasets')
    logger.setLevel(numeric_log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_log_level)

    # Log Handler
    print(f">>> Logging into {log_file_name} with log level {numeric_log_level} - {log_level.upper()}")
    log_file_handler = logging.FileHandler(filename=log_file_name)
    log_file_handler.setFormatter(log_format_str)

    # Formatter
    formatter = logging.Formatter(log_format_str)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(log_file_handler)

    try:
        with open(run_config_file, 'r') as file:
            dsconfig = yaml.safe_load(file)
            logger.info(dsconfig)
    except FileNotFoundError as e:
        logger.error('Error, yaml configuration absent')
        print(f'Yaml configurator absent, does file exist? {e}')
        exit(200)
    except Exception as e:
        print("Exception occured. ", e)
        exit(201)

    logger.info('YAML configurator for data pull processed.')
    logger.info('continuing to process authentication.')


    try:
        if os.path.isfile(auth_config) is False:
            logger.warning("The authorization file not found in args, will use config")
            auth_config = os.path.abspath(dsconfig['run_params']['auth_config_file'])
            print(f"*** Using {auth_config}")
            logger.info('*** Using %s from configurator' % (auth_config))
            if auth_config is None or os.path.isfile(auth_config) is False:
                logger.critical('No config for Authorization file %s is invalid' % (auth_config))
                logger.critical('Auth info is still unavailable')
                raise FileNotFoundError()
        cf = PGConfigFile(auth_config)
        cfg = cf.config
        username = cfg['username']
        password = cfg['password']
        server = cfg['server']
        port = cfg['port']
        database = cfg['database']
    except FileNotFoundError as e:
        logger.error("Auth config File does not exist. %s" % (e.strerror))
        exit(1)

    # Connect to Postgres
    try:
        pg = PGConn(username, password, server, port, database)
        pgconn = pg.pgconn
        assert(pgconn != None)
        logger.info("Database connection is complete")
    except AssertionError as ae:
        logger.critical('Assertion error caught pgconn has issues.')
        exit(100)
    except Exception as e:
        logger.critical('Database connection throws exception %s' % e)
        exit(100)

###

    if data_dir == None:
        print("Data directory is unset, fetching it from config file.")
        logger.info("Data directory is unset, fetching it from config file.")
        data_dir = os.path.abspath(dsconfig['run_params']['data_dir'])
    else:
        data_dir = os.path.abspath(data_dir)
    
    print(f"*** Data directory is set to {data_dir}")
    logger.info('*** Data directory is set to %s' % (data_dir))
    for level in dsconfig.keys():
        print(f"Processing level {level}")
        logging.info("####### %s ########" % (level))
        if level == 'projects':
            for project in dsconfig[level].keys():
                print(f"Processing project {project}")
                if (project is None):
                    raise Exception("Project is None, check yaml file")
                p = PGProject(pgconn, project)
                for query in dsconfig[level][project].keys():
                    created = dsconfig[level][project][query]['created']
                    types = dsconfig[level][project][query]['issuetypes']
                    output_file = os.path.join(data_dir, dsconfig[level][project][query]['outputfile'])
                    print(f"From created date {created} with {types} writing to {output_file}")
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
                            "Project",
                            "Key",
                            "Type",
                            "Status",
                            "Priority",
                            "Severity",
                            "Created",
                            "Updated",
                            "Closed",
                            "Origin",
                            "Reporter", 
                            "Assignee",
                            "Resolution"
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
                s = PGSolution(pgconn, projects=projects)    

                for query in dsconfig[level][solution]['queries'].keys():
                    print(f"Query being processed is {query}")
                    created = dsconfig[level][solution]['queries'][query]['created']         
                    types = dsconfig[level][solution]['queries'][query]['issuetypes']
                    output_file = os.path.join(data_dir, dsconfig[level][solution]['queries'][query]['outputfile'])
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
                            "Project",
                            "Key",
                            "Type",
                            "Status",
                            "Priority",
                            "Severity",
                            "Created",
                            "Updated",
                            "Closed",
                            "Origin",
                            "Reporter", 
                            "Assignee",
                            "Resolution"
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

