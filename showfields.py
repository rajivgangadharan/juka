from jira import JIRA

options = {'server': 'https://jira.atlassian.com',
	   'user':'h140715',
	   'password':'Pokemon74#'}
jira = JIRA(options)

for i in jira.fields():
    print(i['name']+' : '+i['id'])
for i in jira.fields():
	if (i['name'] == 'Story Points'):
		print(i['id'])
		print(i)
		print("\n")
