from utils import Issue, JiraConn, Epic, ConfigFile
from functools import wraps
import argparse
import csv


def csvfy(csv_file):
	def csvfy4dict(function_returning_list_of_dict):
		@wraps(function_returning_list_of_dict)
		def wrapper(*args, **kwargs):
			dlist = []
			d = {}
			open(csv_file, 'w').close() # Zero Out the file
			f = open(csv_file, 'a')
			list_of_dict = function_returning_list_of_dict(*args, **kwargs)
			# Decide the heading of the csv_file
			l = list_of_dict[0] #Picks only the first in the list of dict
			key = [k for k in l.keys()][0] # Gets the key
			value = l[key] #get the dict which is the value of the list of dict
			field_names = value.keys() # Gets the keys of the first dict
			w = csv.DictWriter(f, fieldnames=field_names, delimiter=',')
			w.writeheader() # Writes the header
			# Now to write the rest of the records
			for d in list_of_dict:
				key = [k for k in d.keys()][0]
				value = d[key] # This is the dict which needs to be written as csv line
				print(value)
				w = csv.DictWriter(f, value.keys())
				w.writerow(value)
			f.close()
		return(wrapper)
	return(csvfy4dict)

@csvfy("epicsinfo.csv")
def get_data_for_epics_pi(jira, pi_string, args):
	epic_data = []
	for issue_key in args:
		e = {}
		try:
			ed = Epic(jira, issue_key)
			e[ed.i.key] = {'key':ed.i.key,
							'closed_story_point_aggregate':ed.closed_story_point_aggregate,
							'story_point_aggregate':ed.story_point_aggregate,
							'bottom_up_estimate_for_planned_iteration':\
								ed.get_bottom_up_estimate_for_planned_iteration(pi_string)}
			epic_data.append(e)
		except ZeroDivisionError as err:
			print("Error instantiating Epic Class")
			raise
	return(epic_data)

@csvfy("epicsinfo.csv")
def get_data_for_epics(jira, args):
	epic_data = []
	for issue_key in args:
		e = {}
		try:
			ed = Epic(jira, issue_key)
			e[ed.i.key] = {'key':ed.i.key,
							'closed_story_point_aggregate':ed.closed_story_point_aggregate,
							'story_point_aggregate':ed.story_point_aggregate}
			epic_data.append(e)
		except ZeroDivisionError as err:
			print("Error instantiating Epic Class")
			raise
	return(epic_data)

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Pull data into csv file for all Epic')
	parser.add_argument('-E', '--epics', nargs='+', help="List of Epics", required=True)
	parser.add_argument('-P', help="Planned Iteration")
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
	issue_keys = args.epics
	pi_string = args.P
	jc = JiraConn(username, password, server)
	if(pi_string):
		get_data_for_epics_pi(jc.jira, pi_string, issue_keys)
	else:
		get_data_for_epics(jc.jira, issue_keys)

if __name__ == '__main__':
	main()
