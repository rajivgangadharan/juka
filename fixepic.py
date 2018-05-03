from utils import Issue, JiraConn, Epic, ConfigFile
import argparse

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Fix data in a Epic for both Epic and Stories')
	parser.add_argument("action", choices = ('change','show'))
	parser.add_argument('-i', '--issues', nargs='+', help="Provide Issue Key/s", required=True)
	parser.add_argument('-P', '--planned_iteration', help="Planned Iteration")
	parser.add_argument('-T','--teams', help="Teams")
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
	pi_string = args.P
	jc = JiraConn(username, password, server)
	action = args.action
	for issue_key in issues:
		e = Epic(jc.jira, issue_key)
		if (args.action == "change"):
			e.fix_estimate(pi_string)
			if (args.planned_iteration):
				e.scope(args.planned_iteration)
			if (args.teams):
				for team in arg.teams:
					e.assign_team(args.team)
		else:
			e.print_issues()
if __name__ == '__main__':
	main()
