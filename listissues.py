from utils import RunParams, JiraConn, DeferredEpics, Project
import argparse 

def main():
	rp = RunParams()
	
	username = password = server = None
	parser = argparse.ArgumentParser(description='Query and update issues')
	parser.add_argument('-u', help="Provide User Name")
	parser.add_argument('-p', help="Provide Password")
	parser.add_argument('-s', help="Provide Server URL")
	parser.add_argument('-i', help="Provide Issue Key to be Scoped")
	parser.add_argument('-P', help="Provide Project Name")
	args = parser.parse_args()
	username = args.u
	password = args.p
	server = args.s
	issue_key = args.i
	project_string = args.P
	try:
		assert(rp.username != None and rp.password != None and rp.server != None)
	except AssertionError as a:
		print("AssertionError {:s}/{:s}@{:s}".format(rp.username, rp.password, rp.server))
		exit(1)
	jc = JiraConn(rp.username, rp.password, rp.server)
	p = Project(jc.jira, project_string)
	
	if __name__ == '__main__':
		main()

