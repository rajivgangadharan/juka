import argparse, sys
from utils import Issue, JiraConn, ConfigFile, Metrics

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Show all boards in JIRA')
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
	m = Metrics(jc.jira)
	m.list_boards()

if __name__ == '__main__':
	main()
