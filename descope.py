#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  descope.py
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

from utils import Issue, JiraConn, ConfigFile
import argparse
import sys

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Get all issues/stories for an Epic')
	parser.add_argument('-i', help="Provide Issue Key", required=True)
	cfg = None
	try:
		cf = ConfigFile('config.yaml')
		cfg = cf.config
		username = cfg['username']
		password = cfg['password']
		server = cfg['server']
	except FileNotFoundError as e:
		print("Config File does not exist, falling back to argument parsing")
		parser.add_argument('-u', help="Provide User Name")
		parser.add_argument('-p', help="Provide Password")
		parser.add_argument('-s', help="Provide Server URL")
	args = parser.parse_args()
	if (cfg is None):
		username = args.u
		password = args.p
		server = args.s
	issue_key = args.i
	jc = JiraConn(username, password, server)
	issue = Issue(jc.jira, issue_key)
	issue.descope()

if __name__ == '__main__':
	main()
