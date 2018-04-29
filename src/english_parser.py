from stemming.porter import stem
import json
import re
import pickle

class English_Parser():

    def __init__(self):
        self.stopWords = []

    def load_stop_words(self,file="data/metadata/stopWords.txt"):
        f = open(file)
        content = f.read().decode('utf-8')
        words = content.split('\n')
        for w in words:
            self.stop_words.add(w.strip())

    def read(self, file_name, timelength):

        with open(file_name, 'rb') as f:
            data = json.load(f)

        vocabulary = {}
        tempLine = []
        lineno = 0
        for line in data:
            temp = {}

            cmnt = re.split(r'[^A-Za-z]+', line["message"])

            words = []
            for word in cmnt:
                word = word.lower()
                if word not in self.stopWords:
                    word = stem(word)
                    words.append(word)
                    if word not in vocabulary:
                        vocabulary[word]=0

            if len(words) != 0:
                temp["time"] = line["time"]
                temp["lineno"] = lineno
                temp["text"] = words
                tempLine.append(temp)
            lineno += 1


        lines=sorted(tempLine, key= lambda e:(e.__getitem__('time')))
        self.store(lines,timelength)
        return lines,timelength,vocabulary

    def store(self,lines,timelength):
        fw = open("data/var/lines", "wb")
        fv = open("../lines2.json", "wb")
        json.dump({"lines":lines,"timelength":timelength}, fv)
        pickle.dump({"lines":lines,"timelength":timelength},fw)
        fw.close()

    def run(self,file_name,timelength):
        self.load_stop_words()
        return self.read(file_name,timelength)
