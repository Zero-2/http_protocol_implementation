import os
import re
file = "/var/www/text.csv"
filename = os.path.splitext(file)
if(filename[1] == ".csv"):
    newname = filename[0] + ".html"
print(newname)
# fliesion = os.splitext(filename)
# print(fliesion)
# newname = portion[0] + ".txt"
# os.rename(filename,newname)