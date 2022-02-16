python3 ../listissues.py  --project OP \
--query 'project = "OP" AND Type in ("Epic","Story") AND createdDate >= "2020/05/01"' \
--output '../../DataSets/Opics_Delivery.csv' --max-rows 10000 --batch-size=25
python3 ../listissues.py  --project OP \
--query 'project = "OP" AND Type in ("Defect") AND createdDate >= "2020/05/01"' \
--output '../../DataSets/Opics_Defects.csv' --max-rows 10000 --batch-size=25
