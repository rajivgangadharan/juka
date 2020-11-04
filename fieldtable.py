#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fieldtable.py
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
#     Shows the fields in jira 
###############################################################################
from utils import Issue, JiraConn, ConfigFile
import argparse
import sys

class FieldTable:
	jc = None # Initializing the jira connector
	ft = {} # The field table dict

	def __init__(self):
		self.connect2jira()
		self.construct_field_table()

	def connect2jira(self):
		username = password = server = None
		cfg = {}
		try:
			cf = ConfigFile('config.yaml')
			cfg = cf.config
			username = cfg['username']
			password = cfg['password']
			server = cfg['server']
		except FileNotFoundError as e:
			print("Config File does not exist" + e.strerror)
			raise
		self.jc = JiraConn(username, password, server)

	def construct_field_table(self):
		# Will construct a dict using jira.fields()
		for field in self.jc.jira.fields():
			key = field['name']
			value = field['id']
			self.ft[key] = value

	def persist_field_table(self, file_name):
		# Will write the field table (ft) to file "field.table"
		with open("field.table", "w") as ft:
			for key, value in self.ft:
				print(key + ':' + value, file=ft)

def main():
	ft = FieldTable()
	ft.connect2jira()
	ft.construct_field_table()
	ft.persist_field_table()


if (__name__  == '__main__'):
	main()