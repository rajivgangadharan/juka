python3 listissues.py  --project OP \
--query 'status=Closed and Type in (Epic,Story,Defect)  and "Closed Date">"2020/01/01" ' \
--output '../R/opics.jira.dataset' --max-rows 5000
