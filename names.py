import json
import csv
import unidecode
import re
import csv
from bs4 import BeautifulSoup
import requests
import time

def get(url,count=0):
    if count>3:
        return None
    try:
        return requests.get(url)
    except Exception as e:
        print("# ",e)
        time.sleep(1)
        return get(url,count+1)

def alphas_only(input):
    words = []
    regex = re.compile("[a-zA-Z-']+")
    for word in input.split(" "):
        words.append("".join(regex.findall(unidecode.unidecode(word))))
    return " ".join(words).strip()

def strip_entities(input):
    regex = re.compile("\&[A-z]+\;")
    return re.sub(regex, ' ', input)

def strip_parentheticals(input):
    preprocess = input
    for c in ["-"]:
        preprocess = preprocess.replace(c," ")
    for c in ["II", "III", "IV"]:
        preprocess = preprocess.replace(c,"")
    return re.sub("[\(\[].*?[\)\]]", "", preprocess)

# Given a list of words which may contain a name
# and a list of initials and a surname, return the full name.
# This is a horrible, messy pile of spaghetti
def match_name_to_initials(initials,surname, words):
    # Remove common label words
    STOPWORDS = ["author","authors","first","name","by","firstname", "editor"]
    for i in range(len(words)):
        if words[i].lower() in STOPWORDS:
            words[i] = ""
    # If more than one initial, assume that full names will EITHER have:
    # all initials or *only* the first initial. No partial initial matches.  
    if len(initials) > 1:
        i1 = "".join(
            [word[0].lower() if word else " " for word in words[1:len(initials)+1]])
        i2 = "".join(
            [word[0].lower() if word else " " for word in words[len(initials)+2:]])
        if "".join(initials).lower() == i1:
            return [words[len(initials)+1]]+words[1:len(initials)+1]
        elif "".join(initials).lower() == i2:
            return [words[len(initials)+1]]+words[len(initials)+2:]
        elif i1[-1] == initials[0].lower():
            return [words[len(initials)+1]]+[words[len(initials)-1]]
        elif i2[0] == initials[0].lower():
            return [words[len(initials)+1]]+[words[len(initials)+2]]
    # If we started with only a single initial,
    # maybe there's a middle name or initial we're missing
    # It can be the first or last word or the second word with a middle initial.
    # Discount multiple missing middle initials.
    else:
        # if the first word, then perhaps the input omits a middle initial
        if words[0] and words[0][0].lower() == initials[0].lower():
            return [words[len(initials)+1]]+words[:2]
        if words[1] and words[1][0].lower() == initials[0].lower():
            return [words[len(initials)+1]]+[words[1]]
        if words[-1] and words[-1][0].lower() == initials[0].lower():
            return [words[len(initials)+1]]+[words[-1]]
    return None


# print(match_name_to_initials(['D', 'T'], "Aitken", [
#     '', '', '', 'Aitken', 'DT', '2016']))
# print(match_name_to_initials(['C', 'W'], "Gowans", [
#       'By', 'Christopher', 'W', 'Gowans', 'Edition', '1st']))
# print(match_name_to_initials(
#     ['R'], "Repetti", ['Rick', 'Wick', 'Repetti', 'if']))
# exit()


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

gs_namemap = {gs_name(name):name for name in gendermap}
gs_namemap.update({gs_name_single_initial(name): name for name in gendermap})
gs_gendermap = {gs_name(name):gendermap[name] for name in gendermap}
gs_gendermap.update({gs_name_single_initial(name):gendermap[name] for name in gendermap})

def map_gender(name):
    if name in gs_gendermap:
        return gs_gendermap[name]
    else:
        return "UNKNOWN"


matched_citations = []
unmatched_citations = []

with open("JIABS2010-1559678685.json") as datafile:
    data = json.load(datafile)
    
    with open('network.csv', 'w', newline='') as csvfile, open("cite_names.csv", mode="w") as cite_names_file:
        csvwriter = csv.writer(csvfile, dialect='excel')
        cite_names_writer = csv.writer(cite_names_file, dialect='excel')
        header = ['author', 'author gender','citation author','citation author gender', 'citation title', 'citation journal','citation url' ]
        csvwriter.writerow(header)

        for datum in data.values():
            authors = []
            for author in datum["docinfo"]["bib"]["author"].split(" and "):
                authors.append(author)
            citations = []
            for c in datum["citedby"]:
                for citation_author in c["bib"]["author"].split(" and "):
                    if citation_author not in authors:
                        if "url" not in c["bib"]:
                            if "eprint" in c["bib"]:
                                c["bib"]["url"] = c["bib"]["eprint"]
                            else:
                                c["bib"]["url"] = "NO URL"
                        if "journal" not in c["bib"]:
                            c["bib"]["journal"] = "NO JOURNAL"
                        if "title" not in c["bib"]:
                            c["bib"]["title"] = "NO TITLE"
                        citations.append({"author":citation_author,"title":c["bib"]["title"],"journal":c["bib"]["journal"],"url":c["bib"]["url"]})
            
            for author in authors:
                for citation in citations:
                    if map_gender(citation["author"]) == "UNKNOWN":
                        unmatched_citations.append(citation)
                    else:
                        matched_citations.append(citation)
                    csvwriter.writerow(
                        [author, map_gender(author), citation["author"], map_gender(
                            citation["author"]), citation["title"], citation["journal"], citation["url"]]
                        )
    
    with open("unmatched_citations.csv", mode="w") as citation_file, open("found_citation_names.csv", mode="w") as foundfile:
        citation_csvwriter = csv.writer(citation_file, dialect='excel')
        found_names_csvwriter = csv.writer(foundfile, dialect='excel')
        matched_names = {}
        matched_names_citations = {}
        for citation in unmatched_citations:
            if "url" in citation:
                long_name = None
                if citation["url"].endswith(".pdf"):
                    print("* Ignoring PDF")
                    continue
                # print(citation["url"])
                response = get(citation["url"])
                if not response:
                    print("* No response received after retries")
                    continue
                if "text/html" not in response.headers['Content-Type']:
                    print("* Response Content-Type is not text/html")
                    continue
                html = response.text
                soup = BeautifulSoup(html, features="html.parser")
                text = soup.get_text(" ")
                surname = citation["author"].split()[-1]
                initials = [i for i in citation["author"].split()[0]]
                words = [" "]*len(initials) + text.split() + \
                    [" "]*len(initials)
                print(initials, surname)
                found_possible = False
                for i in range(len(words)):
                    words[i] = alphas_only(strip_entities(words[i]))
                    if words[i].lower() == alphas_only(surname.lower()) and i > len(initials)+1 and i+len(initials) < len(words):
                        name_words = words[i-len(initials)-1:i+len(initials)+1]
                        found_possible = True
                        # print(name_words)
                        long_name = match_name_to_initials(
                            initials, surname, name_words)
                        if long_name:
                            ln_str = long_name[0]+", "+" ".join(long_name[1:])
                            if citation["author"] in matched_names:
                                matched_names[citation["author"]
                                              ].add(ln_str)
                            else:
                                matched_names[citation["author"]
                                              ] = {ln_str}
                            break
                print("=> ",long_name)
            if long_name:
                ln_str = long_name[0]+", "+" ".join(long_name[1:])
                citation_csvwriter.writerow(
                    [citation["author"], ln_str, "", citation["title"],
                        citation["journal"], citation["url"]]
                )
            else:
                citation_csvwriter.writerow(
                    [citation["author"], "UNKNOWN", "",citation["title"],
                        citation["journal"], citation["url"]]
                )
        for short_name in matched_names:
            for ln in matched_names[short_name]:
                found_names_csvwriter.writerow([short_name, ln]
            )
