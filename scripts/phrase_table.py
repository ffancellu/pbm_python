#-*- coding:utf-8 -*-

import codecs
from nltk import ngrams

class PhraseTable:

    def __init__(self,filename):

        self.filename = filename
        self.trie = {}

    def populate_trie(self):

        fstream = codecs.open(self.filename,'rb',encoding='utf-8')
        for line in fstream:
            line_str = line.strip().split(' ||| ')
            s,t,p = line_str[0],line_str[1],float(line_str[2])
            self.insert(s,t,p)

    def insert(self,s,t,p):

        source_spl = s.split()
        #print s,t,p
        current = self.trie
        for i in range(len(source_spl)):
            current = current.setdefault(source_spl[i],{})
            if i == len(source_spl)-1:
                if not current.has_key('t p'):
                    current['t p'] = []
                current['t p'].append((t,p))
            
        
    def retrieval(self,ng):

        current = self.trie
        for i in range(len(ng)):
            if current.has_key(ng[i]):
                current = current[ng[i]]
            else:
                return [('Nothing found',0.0)]
        result = current['t p']
        return result

    def test(self):

        print self.trie['der']

    def return_ngrams(self,string):

        return map(lambda x: list(x),reduce(lambda x,y:x+y,(map(lambda x: ngrams(string.split(),x),[4,3,2,1]))))

    def find_phrases(self,string):

        ngs = self.return_ngrams(string)
        for ng in ngs:
            print ng
            results = self.retrieval(ng)
            for result in results:
                print '%s ---> %s | %.2f' % (' '.join(ng),result[0],result[1])         

if __name__=="__main__":
    pt = PhraseTable("../data/small-phrase-table")
    pt.populate_trie()
    pt.test()  