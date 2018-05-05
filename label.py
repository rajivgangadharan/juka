from utils import Issue, JiraConn, ConfigFile
import argparse
import sys

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Tagging and Untagging of Jira issues')
	parser.add_argument('action', choices=("tag","detag","print"), help="Provide action")
	parser.add_argument('-i', nargs='+', help="Provide Issue Key", required=True)
	parser.add_argument('-T', '--tags', nargs='+', help="List of Tags", required=False)
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
	issues = args.i
	try:
		assert(username != None and password != None and server != None)
	except AssertionError as a:
		print("None username, password, issue, release and/or server")
		exit(1)
	jc = JiraConn(username, password, server)
	for issue_key in issues:
		issue = Issue(jc.jira, issue_key)
		tags = args.tags
		if (args.action == "tag"):
			issue.tag(tags)
		elif (args.action == "detag"):
			issue.detag(tags)
		else:
			issue.show_tags()


if __name__ == '__main__':
	main()
