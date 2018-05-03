# @Author: Rajiv Gangadharan
# @Date:   2017-12-16T14:03:02+05:30
# @Email:  rajiv.gangadharan@gmail.com
# @Project: JUKA (Jira Utility for All)
# @Filename: scope.py
# @Last modified by:   Rajiv Gangadharan
# @Last modified time: 2017-12-20T11:55:40+05:30



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
	parser = argparse.ArgumentParser(description='Scope and Descope Issues (Stories, Epics etc.)')
	parser.add_argument('--issues','-I', nargs = '+', help="Provide Issue Key or list thereof", required=True)
	parser.add_argument('--planned_iteration', '-P', help="PI - uses the Planned iteration field")
	#parser.add_argument('--release', '-R', help="Release String - uses the Jira Planned Iteration field")
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
	pi_string = args.planned_iteration
	#release_string = args.release
	jc = JiraConn(username, password, server)
	for issue in issues:
		print("Scoping issue {} for {}".format(issue, pi_string))
		issue = Issue(jc.jira, issue)
		issue.scope(pi_string)
		#issue.set_release(release_string)

if __name__ == '__main__':
	main()
