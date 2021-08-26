#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pgutils.py
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

import psycopg2
import argparse
import os.path
from pathlib import Path
import yaml

class PGConfigFile:
    config = {}
    file_string = ""

    def __init__(self, file_string):
        self.config = {}
        self.file_string = file_string
        if (self.is_exists()):
            self.read()

    def read(self):
        with open(self.file_string, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, yaml.SafeLoader)
        print(cfg)
        self.config['username'] = cfg['pg']['username']
        self.config['password'] = cfg['pg']['password']
        self.config['server'] = cfg['pg']['server']
        self.config['port'] = cfg['pg']['port']
        self.config['database'] = cfg['pg']['database']

    def is_exists(self):
        f = Path(self.file_string)
        if f.is_file():
            return True
        else:
            return False

class PGConn:
    pgconn = None
    username = None
    password = None
    server = None
    options = None

    def __init__(self, username, password, server, port, database):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.database = database
        if not isinstance(self.port, int):
            print("Error instantiating PGConn")
            raise Exception("Port is not an integer {}.".format(self.port))
        self.pgconn = self.pg_connect()


    def pg_connect(self):
        assert(self.server != None and self.port != None)
        try:
            conn = psycopg2.connect(
                host=self.server,
                database=self.database,
                user=self.username,
                password=self.password,
                port=self.port)
        except psycopg2.OperationalError as oe:
            print("Exception caught! %s"% (oe.pgerror))
            print("Connection parameters %s@%s:%s db: (%s) " % (self.username, self.server, self.port, self.database))
            raise
        except psycopg2.ProgrammingError as pge:
            print("Caught error %s" % (pge.pgerror))
            raise
        except psycopg2.DatabaseError as dbe:
            print("Failed PGconnect %s" % (dbe.pgerror))
            raise
        return conn

    def pg_disconnect(self):
        assert(self.server != None and self.port != None)
        try:
            self.pgconn.close()
        except psycopg2.DatabaseError as dbe:
            print("Failed PGconnect - {:d} - {:s}".format(dbe.pgcode, dbe.pgerror))
            pass


class RunParams:
    mode = None # Query --query or Fix --fix
    project = None #
    sprint = None #
    username = None
    password = None
    server = None

    def __init__(self):
        self.parse_params()

    def parse_params(self):
        parser = argparse.ArgumentParser(description='Query and update issues')
        parser.add_argument('-u',
                help="Provide User Name")
        parser.add_argument('-p',
                help="Provide Password")
        parser.add_argument('-s',
                help="Provide Server URL")
        parser.add_argument('project_sprint',
                help="Specify the project and sprint in the form project:sprint")
        args = parser.parse_args()
        self.username = args.u
        self.password = args.p
        self.server = args.s
        (self.project, self.sprint) = args.project_sprint.split(":")
