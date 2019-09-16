import json
import csv
import unidecode
import re
import csv

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

def gs_name_single_initial(name):
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
gs_gendermap2 = {gs_name_single_initial(name):gendermap[name] for name in gendermap}

def map_gender(name):
    if name in gs_gendermap:
        return gs_gendermap[name]
    elif name in gs_gendermap2:
        return gs_gendermap2[name]
    else:
        return "UNKNOWN"

with open("JIABS2010-1559678685.json") as datafile:
    data = json.load(datafile)
    
    with open('network.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel')
        header = ['author', 'author gender','citer']
        csvwriter.writerow(header)

        for datum in data.values():
            authors = []
            for author in datum["docinfo"]["bib"]["author"].split(" and "):
                authors.append(author)
            citers = set()
            for citation in datum["citedby"]:
                for author in citation["bib"]["author"].split(" and "):
                    if author not in authors:
                        citers.add(author)
            for author in authors:
                for citer in citers:
                    csvwriter.writerow([author,map_gender(author),citer])
                
