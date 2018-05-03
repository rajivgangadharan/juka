from utils import JiraConn, Metrics, SprintBoard
import argparse

def main():
	username = password = server = None
	parser = argparse.ArgumentParser(description='Get Story Point Estimates')
	parser.add_argument('-u', help="Provide User Name")
	parser.add_argument('-p', help="Provide Password")
	parser.add_argument('-s', help="Provide Server URL")
	parser.add_argument('-b', help="Provide Board ID (Numerical)")
	args = parser.parse_args()
	username = args.u
	password = args.p
	server = args.s
	board_id = args.b
	try:
		assert(username != None and password != None and server != None)
	except AssertionError as a:
		print("None username, password and/or server")
		exit(1)
	jc = JiraConn(username, password, server)
	sb = SprintBoard(jc.jira, board_id)
	sb.list_sprints()



if __name__ == '__main__':
	main()
