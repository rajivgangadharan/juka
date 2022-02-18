coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
import re
regex = r"[0-9] - "
test_str = "3 - Medium"
subst = ""
# You can manually specify the number of replacements by changing the 4th argument
result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
if result:
    print (result)
