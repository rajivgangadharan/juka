python3 listissues.py  --project OP \
--query 'project = "OP" AND Type in ("Epic") AND createdDate >= "2020/01/01"' \
--output '../R/Opics_2021-06-17_Epics.csv' --max-rows 10000 --batch-size=25
python3 listissues.py  --project OP \
--query 'project = "OP" AND Type in ("Defect") AND createdDate >= "2020/01/01"' \
--output '../R/Opics_2021-06-17_Defects.csv' --max-rows 10000 --batch-size=25
