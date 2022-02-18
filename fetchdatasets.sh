#!/usr/bin/bash
python fetchdataset.py  --max-rows 1500 --batch-size=1000
if [ $? -ne 0 ]; then
  echo "$0 - data extract failed."
  exit 1
else
  echo "$0 - successful"
fi
