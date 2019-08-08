import json
import csv
import unidecode
import re

def alphas_only(input):
    words = []
    regex = re.compile("[a-zA-Z-]+")
    for word in input.split(" "):
        words.append("".join(regex.findall(unidecode.unidecode(word))))
    return " ".join(words).strip()

def strip_parentheticals(input):
    return re.sub("[\(\[].*?[\)\]]", "", input)

def gs_name(name):
    surname = alphas_only(name.split(",")[0])
    fname = name.split(",")[1] if len(name.split(","))>1 else ""
    initials = alphas_only("".join([n[0] if n else "" for n in strip_parentheticals(fname).strip().split(" ")]))
    if initials:
        gs_name = initials+" "+surname
    else:
        gs_name = surname
    return(gs_name)


with open('names.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    gendermap = {row[0]:row[1] if row[1] else "NULL" for row in csvreader}

dupe = {}

for name in gendermap:
    alphas_name = alphas_only(strip_parentheticals("".join(name.split(",")[0:2])))
    print(alphas_name)
    if gs_name(name) not in dupe:
        dupe[gs_name(name)] = [alphas_name]
    elif alphas_name not in dupe[gs_name(name)]:
        dupe[gs_name(name)].append(alphas_name)

for d in dupe:
    if len(dupe[d])>1:
        print(d,": ",dupe[d])

exit()

# with open("names.csv", mode='r') as csvfile:
#     with open("JIABS2010-1559678685.json") as datafile:
#         data = json.load(datafile)
#         for datum in data.values():
#             if ";" in datum["csv"][0]:
#                 continue
            
#             name = datum["csv"][0]
#             gender = gendermap[name]
