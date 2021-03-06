from collections import defaultdict
import csv
import re
import sys

def build_data(fname,preprocess=True):
    """
    Reads a CSV file with headers 'labels' and 'text' (containing label string and text respectively)
    and outputs sentences, vocab and labels
    :param fname: file name to read
    :param preprocess: should data be preprocessed
    :return: sentences is a list of dictionary (a format which NNTrainer accepts) [{'text': <text>, 'y':<label>},...]
    """
    sentences = []
    vocab = defaultdict(float)
    labels=[]
    rows = []
    count = 0
    csv.field_size_limit(sys.maxsize)
    with open(fname, "rb") as f:
        dialect = csv.Sniffer().sniff(f.readline())
        f.seek(0)
        reader = csv.DictReader((line.replace('\0','') for line in f),None,None,None,dialect)
       
        for line in reader:
            label = line['labels']
            print count
            count = count + 1
            rows.append((label,line['text']))  # Tuple: (label,text)
            labels=labels+[label]
    labels = list(set(labels))
    labels.sort()
    labelIdToLabel = dict(zip(labels,range(len(labels))))
    for row in rows:
        y=labelIdToLabel[row[0]]
        rev = []
        rev.append(row[1].strip())
        if preprocess==True:
            orig_rev = clean_str(" ".join(rev))
        else:
            orig_rev = rev[0]

        words = set(orig_rev.split())
        for word in words:
            vocab[word] += 1

        datum  = {"y":y,
                  "text": orig_rev,
                  "num_words": len(orig_rev.split())}
        sentences.append(datum)
    return sentences, vocab, labels


def clean_str(str):
    """
    Tokenization/string cleaning. This is specific to tweets, but can be applied for other texts as well.
    """
    str=str+" "
    str=re.sub("http[^ ]*[\\\]","\\\\",str)                    #Remove hyperlinks
    str=re.sub("http[^ ]* "," ",str)                           #Remove hyperlinks
    str=str.replace('\\n',' ')
    arr=re.findall(r"\w+(?:[-']\w+)*|'|[:)-.(]+|\S\w*", str)   #Single punctuation mark is removed, smileys remain intact
    arr=[i for i in arr if len(i)>1 and i[0]!='@']             #Remove words starting with @ (Twitter mentions)
    arr=[i if i[0]!='#' else i[1:] for i in arr]               #Remove '#' from hashtags
    #arr=[i for i in arr if i!='http' and i!='com' and i!='org']
    res=" ".join(arr)
    return res.lower().strip()
