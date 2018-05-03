from utils import Issue, JiraConn, ConfigFile
from jira import JIRA, JIRAError
import argparse

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Get Story Point Estimates')
	parser.add_argument('-u', help="Provide User Name")
	parser.add_argument('-p', help="Provide Password")
	parser.add_argument('-s', help="Provide Server URL")
	parser.add_argument('-i', help="Provide Issue Key")
	parser.add_argument('-E', help="Provide new storypoint Estimate")
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
	try:
		assert(username != None and password != None and server != None and issue_key != None)
	except AssertionError as a:
		print("None username, password and/or server or issue_key")
		print('Usage: {:s} [-u <user> -p <password> -s <server>] -i <issue key> [-E <estimate>]')
		exit(1)
	jc = JiraConn(username, password, server)
	issue = Issue(jc.jira, issue_key)
	print("Current Estimate for Issue is ", issue.get_estimate_in_story_points())
	if (args.E):
		try:
			print("New Estimate Provided, Updating.")
			estimate = float(args.E)
			issue.set_estimate_in_story_points(estimate)
		except JIRAError as e: 
			print("New Estimate update failed. {} {}".format(e.status_code, e.text))
			exit(2)
		print("Updated.")


if __name__ == '__main__':
	main()
