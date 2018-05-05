from utils import Issue, JiraConn, ConfigFile
import argparse
import sys

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Jira issues Team Assignment')
	parser.add_argument('action', \
			choices=("assign","unassign","print"), help="Provide action")
	parser.add_argument('-i','--issues', help="Provide Issue Keys", nargs='+', required=True)
	parser.add_argument('-T', '--team', help="Team Code String", required=False)
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
	try:
		assert(username != None and password != None and server != None)
	except AssertionError as a:
		print("None username, password, issue, release and/or server")
		exit(1)
	jc = JiraConn(username, password, server)
	action = args.action
	team = args.team
	for issue_key in issues:
		issue = Issue(jc.jira, issue_key)
		if (action == "assign"):
			issue.assign_team(team)
		elif(action == "print"):
			issue.show_teams()
		elif(action == "unassign"):
			issue.unassign_all_teams()


if __name__ == '__main__':
	main()
