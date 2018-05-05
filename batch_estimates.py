#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  best.py
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
#  The script does either of the two things:
#  1. Option alter - Accepts a key:value pair of JIRA keys and its story point
#     estimate and updates the story point field of the story (the JIRA Key)
#     with the estimate
#  2. Option show - Accepts a list of JIRA Keys (Stories) and prints their
#     story point estimate
###############################################################################
from utils import Issue, JiraConn, ConfigFile
import argparse
import sys

class BatchEstimate:
	total_estimate = 0
	estimates = None
	keys = None
	jc = None

	def __init__(__self__, jc, estimates, keys):
		if (estimates is None and keys is None):
			print("Class cannot be instatiated, both estimates and keys cannot be None")
			raise AssertionError()
		if (estimates):
			assert(keys is None)
			__self__.estimates = estimates
		if (keys):
			assert(estimates is None)
			__self__.keys = keys
		__self__.jc = jc

	def batch_alter(__self__):
		tot = 0
		for e in __self__.estimates:
			key_and_estimate = e.split(':')
			key = key_and_estimate[0]
			estimate = key_and_estimate[1]
			tot += int(0 if estimate is None else estimate)
			issue = Issue(__self__.jc.jira, key)
			issue.set_estimate_in_story_points(int(estimate))
		return(tot)

	def show_estimates(__self__):
		tot = 0
		if (__self__.keys is None):
			print("Keys need to specified to show.")
			raise AssertionError()
		total_estimate = 0
		for key in __self__.keys:
			issue = Issue(__self__.jc.jira, key)
			estimate = issue.get_estimate_in_story_points()
			tot += int(0 if estimate is None else estimate)
			print("{} Est. {}".format(key, estimate))
		return(tot)

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
	be = BatchEstimate(jc, args.estimates, args.keys)
	if (args.action == "show"):
		total_estimate = be.show_estimates()
	elif (args.action == "alter"):
		total_estimate = be.batch_alter()
	print("Total Story Points = {}".format(total_estimate))

if __name__ == '__main__':
	main()
