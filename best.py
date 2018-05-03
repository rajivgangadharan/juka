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

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Batch Get and Set \
			Estimates for Issues (Epics and Stories)')
	parser.add_argument("action", choices=("alter","show"))
	parser.add_argument('--estimates','-E', nargs='+', help="Provide key, \
		estimate pairs in the format key:estimate", required=False)
	parser.add_argument('--keys','-K', nargs='+', help="Provide keys, \
		to show current estimates", required=False)
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
	jc = JiraConn(username, password, server)
	estimates = args.estimates
	keys = args.keys
	if (args.action == "show"):
		if (args.keys is None):
			print("Keys need to specified to show.")
			sys.exit(1)
		if(args.estimates):
			print("Ignoring provided estimates not valid for show option.")
		total_estimate = 0
		for key in args.keys:
			issue = Issue(jc.jira, key)
			estimate = issue.get_estimate_in_story_points()
			total_estimate += int(0 if estimate is None else estimate)
			print("{} Est. {}".format(key, estimate))
	elif (args.action == "alter"):
		total_estimate = 0
		for e in estimates:
			key_and_estimate = e.split(':')
			key = key_and_estimate[0]
			estimate = key_and_estimate[1]
			total_estimate += int(0 if estimate is None else estimate)
			issue = Issue(jc.jira, key)
			issue.set_estimate_in_story_points(int(estimate))
	print("Total Story Points = {}".format(total_estimate))

if __name__ == '__main__':
	main()
