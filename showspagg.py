from utils import Issue, JiraConn, Epic
import argparse

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Get Story Point Estimates')
	parser.add_argument('-u', help="Provide User Name")
	parser.add_argument('-p', help="Provide Password")
	parser.add_argument('-s', help="Provide Server URL")
	parser.add_argument('-i', help="Provide Issue Key")
	args = parser.parse_args()
	username = args.u
	password = args.p
	server = args.s
	issue_key = args.i
	try:
		assert(username != None and password != None and server != None)
	except AssertionError as a:
		print("None username, password and/or server")
		exit(1)
	jc = JiraConn(username, password, server)
	issue = Epic(jc.jira, issue_key)
	print("Bottom Up Estimate is {:f}".format(issue.get_bottom_up_estimate()))


if __name__ == '__main__':
	main()
