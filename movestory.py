#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  movestory.py
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
from utils import Issue, JiraConn, Epic, ConfigFile
import argparse

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Move an Issue to another Epic')
	parser.add_argument('-I', '--issues','--stories', nargs='+', \
				help="Provide Issue Keys", required=True)
	parser.add_argument('-e', '--epic', help="Provide Issue Key", required=True)
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
	issues = args.issues
	epic = args.epic
	jc = JiraConn(username, password, server)
	for issue in issues:
		i = Issue(jc.jira, issue)
		i.set_epic(epic)

if __name__ == '__main__':
	main()
