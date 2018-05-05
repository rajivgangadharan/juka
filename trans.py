#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  scopeutil.py
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
from jira import JIRA, JIRAError

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Get and Set \
			Estimates for Issues (Epics and Stories)')
	parser.add_argument("action", choices=("what","alter"))
	parser.add_argument('-i', help="Provide Issue Key", required=True)
	parser.add_argument('-T','--tid', help="Provide the Transition ID", required=False)
	parser.add_argument('-C','--comment',help="Comment for the transition", required=False)

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
	if(args.action == "what"):
		issue.available_transitions()
	elif (args.action == "alter"):
		try:
			jc.jira.transition_issue(issue.i, str(args.tid))
		except JIRAError as e:
			print("Exception: error is {}-{}".format(e.status_code, e.text))

if __name__ == '__main__':
	main()
