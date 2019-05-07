import porter
import json
import string
import math
import sys
import getopt

p = porter.PorterStemmer()
stopword = set()
with open('stopwords.txt','r') as f:
    for line in f:
    	stopword.add(line.strip())

f = open('lisa.all.txt','r')
division = f.read().split('********************************************')

f1 = open('lisa.queries.txt','r')
querydiv = f1.read().split('#')
stem_freq = {}
stemmed = {}

def prepare(docum):
    dict = {}
    sum = 0
    for i in docum:
        list = []
        division = i.split()
        no = int(division[1])
        for str in division[2:]:
            str = str.lower()
            for s in str:
                if s in string.punctuation:
                    str = str.replace(s,'')
            if str not in stopword:
                if str not in stemmed:
                    stemmed[str] = p.stem(str)
                str = stemmed[str]
                list.append(str)
        sum += len(list)
        dict[no] = list
    avg = sum/len(dict)
    return dict,avg

def preparequery(docum):
    dict = {}
    for i in docum:
        q = set()
        division = i.split()
        no = int(division[0])
        for str in division[1:]:
            str = str.lower()
            for s in str:
                if s in string.punctuation:
                    str = str.replace(s,'')
            if str not in stopword:
                if str not in stemmed:
                    stemmed[str] = p.stem(str)
                str = stemmed[str]
                q.add(str)
        dict[no] = q
    return dict

def BM25(dict, avg, k, b):
    length = len(dict)
    lefts = {}
    right = {}
    for id in dict:
        left = {}
        freq = {}
        for term in dict[id]:
            if term not in freq:
                if term not in stem_freq:
                    stem_freq[term] = 1
                else:
                    stem_freq[term] += 1
                freq[term] = 1
            else:
                freq[term] += 1
        for term in freq:
            left[term] = (freq[term]*(1+k))/(freq[term]+k*((1-b)+b*len(dict[id])/avg))
        lefts[id] = left
    for term in stem_freq:
        rightvalue = math.log((length - stem_freq[term] + 0.5)/(stem_freq[term] + 0.5), 2)
        right[term] = rightvalue
    return lefts,right

def preparesimplequery(query):
    qset = set()
    for i in query:
        if i not in stopword:
            if i not in stemmed:
                stemmed[i] = p.stem(i)
            i = stemmed[i]
            qset.add(i)
    return qset

def similarity(query,docudict,right):
    scoredic = {}
    for doc in docudict:
        score = 0
        for q in query:
            if q in docudict[doc]:
                score += docudict[doc][q] * right[q]
        scoredic[doc] = score
    scoredic = sorted(scoredic.items(), key=lambda d: d[1], reverse=True)
    return scoredic

def manual_print(scoredic,query):
    print('Results for query [', end='')
    for q in query:
        if q != query[-1]:
            print(q, end=' ')
        else:
            print(q, end=']\n\n')
    i = 1
    for tuple in scoredic:
        if i <= 15:
            print(str(i)+' '+str(tuple[0])+' '+str(tuple[1]))
            i+=1
        else:
            print()
            break

def manual():
    doc, avg = prepare(division[:-1])
    lefts, right = BM25(doc, avg, 1, 0.75)
    active = True
    while active:
        message = input("Enter query:")
        if message == "QUIT":
            active = False
        else:
            inputquery = message.split()
            inputset = preparesimplequery(inputquery)
            simpledic = similarity(inputset, lefts, right)
            manual_print(simpledic, inputquery)

def evaluation():
    doc, avg = prepare(division[:-1])
    lefts, right = BM25(doc, avg, 1, 0.75)
    querydic = preparequery(querydiv[:-1])
    feva = open('evaluation_output.txt', 'a')
    for id in querydic:
        simpledic = similarity(querydic[id], lefts, right)
        i = 1
        for s in simpledic[0:15]:
            feva.write(str(id) + ' ' + str(s[0]) + ' ' + str(i) + '\n')
            i += 1
    feva.close()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:")
    except getopt.GetoptError:
        sys.exit(-1)
    for opt, arg in opts:
        if opt in ("-m"):
            if arg == 'manual':
                print('Loading BM25 index from file, please wait.')
                manual()
            elif arg == 'evaluation':
                evaluation()

if __name__ == '__main__':
    main()