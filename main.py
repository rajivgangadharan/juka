from utils import RunParams, JiraConn, DeferredEpics

def main():
	rp = RunParams()
	try:
		assert(rp.username != None and rp.password != None and rp.server != None)
	except AssertionError as a:
		print("AssertionError {:s}/{:s}@{:s}".format(rp.username, rp.password, rp.server))
		exit(1)
	jc = JiraConn(rp.username, rp.password, rp.server)
	#m = Metrics(jc.jira)
	#m.list_boards()
	#print("The Board Name is ", m.get_board_name_by_id(6579))
	#u = DeferredEpics(jc.jira, 'SCCS')
	#u.list_deferred_epics()
	#to_be_deferred_list = ['SCCS-98','SCCS-86']
	#u.descope_specified_deferred_epics(to_be_deferred_list)



if __name__ == '__main__':
	main()
