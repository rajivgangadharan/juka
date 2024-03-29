#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  fetchdataset.py
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

from io import FileIO
from typing import List
from utils import JiraConn, ConfigFile
from project import Project
import sys, yaml, logging
import argparse
from io import FileIO
import re
from typing import List, Any, Union
import commons.fieldfixers

def print_issues_to_file(issues:List, of) -> None:
    assert(issues != None)
    assert(of != None)
    print(f'print_issues_to_file() - writing {len(issues)} issues to file')
    header = [
        "Key",
        "Type",
        "Status",
        "Priority",
        "Created",
        "Updated",
        "Closed",
        "Origin", 
        "Source",
        "Category",
        "Severity",
        "Verified",
        "Resolution"
    ]

    print(*header, sep='\t', file=of)

    for i in issues:
        try:
            categories = commons.fieldfixers.fix_categories(
                    str(i.fields.customfield_13065)
                ) if ( # Category
                    hasattr(i.fields, 'customfield_13065')
                ) else None
            category = categories.pop() if len(categories) > 0 else None
            severity = commons.fieldfixers.strip_numerical_from_severity(
                    str(i.fields.customfield_10200)
                ) if ( #Severity 
                    hasattr(i.fields,'customfield_10200')
                ) else None
            fields = [
                i.key,
                i.fields.issuetype,
                i.fields.status,
                i.fields.priority,
                i.fields.created,
                i.fields.updated,
                i.fields.customfield_13000,
                i.fields.customfield_13405 if ( # Origin
                    hasattr(i.fields,'customfield_13405')) else None,
                i.fields.customfield_10110 if ( # Source
                    hasattr(i.fields, 'customfield_10110')) else None,
                category if ( # Category
                    hasattr(i.fields, 'customfield_13065')) else None,
                severity, # Severity without the numerical part.
                i.fields.customfield_10128 if (  # Verified Date
                    hasattr(i.fields, 'customfield_10128')) else None,
                i.fields.resolution if (  # Resolution
                    hasattr(i.fields, 'resolution')) else None,
            ]
            print(*fields, sep="\t", file=of) 
            print(*fields, sep="\t")
        except AttributeError as ae:
            print(f"Exception caught, missing attribute, {str(ae)}")
            raise
        except UnboundLocalError as ule:
            print(f"Exception caught, unbound local error, {str(ule)}")
            raise
        except Exception as e:
            print(f"Exception caught, {str(e)}")
            raise
    print(f'print_issues_to_file() - done.')

def construct_query_string(config, project, query):
    created = config[project][query]['created']
    types = config[project][query]['issuetypes']
    output_file = config[project][query]['outputfile']
    issuetypes = ', '.join(types)
    if 'filter' in config[project][query]:
        filter = config[project][query]['filter']
        querystr = 'Type in (' + issuetypes + ') AND createdDate >= ' +\
        "\"" + created + "\" AND " + filter
    else: 
        querystr = 'Type in (' + issuetypes + ') AND createdDate >= ' +\
                "\"" + created + "\""               
    
    return querystr     

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
        logging.error("Config File does not exist." + e.strerror)
        exit(1)

    parser = argparse.ArgumentParser(
        prog='fetchdataset',
        description="Assembling a dataset for delivery insights")
    parser.add_argument("--batch-size", 
                        help='Batch size for Jira fetch', 
                        required=False, default=100)
    parser.add_argument("--max-rows", 
                        help='Arrest the number of rows processed', 
                        required=False, default=3000)
    parser.add_argument("--config", 
                        help='Config file (default: fetchdataset.yaml)',
                        required=False, default="fetchdataset.yaml")
    parser.add_argument("--log-level", help="Set your log level.", 
                        required=False, default="INFO")
    args = parser.parse_args()
    max_rows = int(args.max_rows)
    batch_size = int(args.batch_size)
    run_config_file = args.config
    
    # Set up logging
    loglevel = args.log_level
    numeric_log_level = getattr(logging, loglevel.upper())
    if (not isinstance(numeric_log_level, int)):
        raise ValueError("Invalid numeric_log_level : %s" % numeric_log_level)
    logging.basicConfig(filename="fetchdataset.log",
                        level=numeric_log_level,
                        filemode='a',
                        format="%(asctime)s %(message)s",
                        datefmt="%Y:%m:%d %H:%M:%S")
        

    # Connect 
    con = JiraConn(username, password, server).jira # jira conection
    assert(con != None)
    
    try:
        print("YAML configurator not provided,  defaulting to fetchdataset.yaml.")
        with open(run_config_file, 'r') as file:
            dsconfig = yaml.safe_load(file)
        print(dsconfig)
    except FileNotFoundError as e:
        print("Error, yaml configurator absent, does file exist?", e)
        exit(200)
    except Exception as e:
        print("Exception occured " , e)
        exit(201)

    for project in dsconfig:
        p = Project(con, project)
        for query in dsconfig[project].keys():
            querystr = construct_query_string(dsconfig, project, query)
            print(f'Executing {querystr} for {project}')
            issues = p.get_issues_for_query(
                max_rows=max_rows,
                query=querystr,
                block_size=batch_size)
            logging.info("Collected # " + str(len(issues)) + " issues.")
        
            # Check if output file can be successfully opened
            # Opening output file
            output_file = dsconfig[project][query]['outputfile']
            if (output_file is not None):
                    try:
                        print(f'Opening {output_file} for writing')
                        with open(output_file, "w") as of:
                            print_issues_to_file(issues, of)  
                        logging.info("Wrote data file.")               
                    except Exception as e:
                        logging.info("Exception while opening file")
                        sys.exit(1)
                
if __name__ == '__main__':
    main()
