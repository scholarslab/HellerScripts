import json
import csv
import unidecode
import re

def alphas_only(input):
    words = []
    regex = re.compile("[a-zA-Z-']+")
    for word in input.split(" "):
        words.append("".join(regex.findall(unidecode.unidecode(word))))
    return " ".join(words).strip()

def strip_parentheticals(input):
    preprocess = input
    for c in ["-"]:
        preprocess = preprocess.replace(c," ")
    for c in ["II", "III", "IV"]:
        preprocess = preprocess.replace(c,"")
    return re.sub("[\(\[].*?[\)\]]", "", preprocess)
    

def gs_name(name):
    surname = alphas_only(name.split(",")[0])
    fname = name.split(",")[1] if len(name.split(","))>1 else ""

    initials = alphas_only("".join([n[0] if n else "" for n in strip_parentheticals(fname).strip().split(" ")]))
    if initials:
        return initials+" "+surname
    else:
        return surname

def gs_name2(name):
    surname = alphas_only(name.split(",")[0])
    fname = name.split(",")[1] if len(name.split(","))>1 else ""

    initials = alphas_only("".join([n[0] if n else "" for n in strip_parentheticals(fname).strip().split(" ")]))
    if initials:
        return initials[0]+" "+surname
    else:
        return surname
    
    

with open('names.csv', mode='r') as csvfile:
    csvreader = csv.reader(csvfile)
    gendermap = {row[0]:row[1] if row[1] else "NULL" for row in csvreader}

gs_gendermap = {gs_name(name):gendermap[name] for name in gendermap}

gs_gendermap2 = {gs_name2(name):gendermap[name] for name in gendermap}

count = 0
notfound = 0

with open("JIABS2010-1559678685.json") as datafile:
    data = json.load(datafile)
    print("Authors:\n")
    for datum in data.values():
        for author in datum["docinfo"]["bib"]["author"].split(" and "):
            count+=1
            name = gs_name(author)
            if name in gs_gendermap:
                print(name, " : ", gs_gendermap[name])
            elif name in gs_gendermap2:
                print(name, " : ", gs_gendermap2[name])
            else:
                print(name, " : NOT FOUND")
                notfound+=1
    print("Total names: ", count)
    print("Not found names: ", notfound)

    count = 0
    notfound = 0
    print("Citation authors:\n")
    for datum in data.values():
        for citation in datum["citedby"]:
            for author in citation["bib"]["author"].split(" and "):
                count+=1
                name = gs_name(author)
                if name in gs_gendermap:
                    print(name, " : ", gs_gendermap[name])
                elif name in gs_gendermap2:
                    print(name, " : ", gs_gendermap2[name])
                else:
                    print(name, " : NOT FOUND")
                    notfound+=1
    print("Total names: ", count)
    print("Not found names: ", notfound)
    
