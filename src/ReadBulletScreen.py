# -*- coding: utf-8 -*-
import re
import jieba
import jieba.posseg as pseg
import uniout
import copy
import json

try:
    import cPickle as pickle
except ImportError:
    import pickle
class BulletScreen(object):
    def __init__(self):
        self.stop_words= set([
                    " ","the","of","is","and","to","in","that","we","for",\
                    "an","are","by","be","as","on","with","can","if","from","which","you",
                    "it","this","then","at","have","all","not","one","has","or","that","什么","姐姐","一个"
                    ])


    def load_stop_words(self,file="data/metadata/stopWords.txt"):
        f = open(file)
        content = f.read().decode('utf-8')
        words = content.split('\n')
        for w in words:
            self.stop_words.add(w.strip())


    def read(self,file_name,timelength):

        #f = open("data/1993410.txt", "r")
        #timelength = 5640
        # f = open("data/5077534.txt", "r")
        # timelength = 4740
        f = open(file_name, "r")
        #timelength = 2582

        tempLine=[]
        #vocabulary=set()
        vocabulary = {}
        jieba.load_userdict("data/metadata/user_dict.txt")
        for lineNo,line in enumerate(f.readlines()):
            pattern=re.compile("^<d p=\"(.+)\">(.+)</d>")
            m=pattern.match(line)
            if m:
                print ((m.group()))
                print int(float(m.group(1).split(',')[0]))
                exit()
                temp={}
                temp={"time":int(float(m.group(1).split(',')[0])), \
                                   "text":[word  for word,flag in pseg.cut(m.group(2))  \
                                           if word not in self.stop_words and flag not in \
                                           ["m","w","g","c","o","p","z","q","un","e","r","x","d","t","h","k","y","u","s","uj","ul","r","eng"] ],
                                   "lineno":lineNo+1}

                if len(temp["text"])>3:
                    tempLine.append(temp)
                    for item in temp["text"]:
                        if item not in vocabulary:
                            vocabulary[item]=0
        #print(len(tempLine))
        lines=sorted(tempLine, key= lambda e:(e.__getitem__('time')))
        # with open("../line.json", 'w') as f:
        #     json.dump(lines, f)

        # print vocabulary
        # print  "vocabulary size: %d " % len(vocabulary)
        # print  "video comment size: %d " % len(lines)
        # print  lines[12]
        self.store(lines,timelength)
        return lines,timelength,vocabulary

    def store(self,lines,timelength):
        fw = open("data/var/lines", "wb")
        # fv = open("../lines1.json", "wb")
        # json.dump({"lines":lines,"timelength":timelength}, fv)
        pickle.dump({"lines":lines,"timelength":timelength},fw)
        fw.close()

    def run(self,file_name,timelength):
        self.load_stop_words()
        return self.read(file_name,timelength)

if __name__=="__main__":
    filename="data/1.txt"
    timelenth=2582
    print BulletScreen().run(filename,timelenth)
