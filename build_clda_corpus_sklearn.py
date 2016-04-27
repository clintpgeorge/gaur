# -*- coding: utf-8 -*-
"""This script creates datsets to evaluate the c-LDA model 

Created on: Sun Mar 01 20:50:00 2015
Last modified on: Thu Mar 31 09:05:00 2016  

@author: Clint P. George 
"""


import codecs 
from os.path import exists, join
from os import mkdir
from sklearn.datasets import fetch_20newsgroups
from gensim import corpora
from utils_text import stop_words, is_date, is_numeric, STRIP_CHARS
from collections import defaultdict


class TFCorpusGenerator(object):
    '''A Generator class for the term-frequency (TF) corpus. It helps a lazy 
    loading for documents in the corpus
    '''        
    def __init__(self, dictionary, doc_tokens):
        """Class constructor 
        
        Arguments: 
        dictionary - a dictionary object 
        docs - a list of tokenized documents 
        
        """            
        self.doc_tokens = doc_tokens               
        self.dictionary = dictionary
    def __iter__(self):    
        for tokens in self.doc_tokens:
            yield self.dictionary.doc2bow(tokens)






'''
Running configurations 
'''


categories = [
 'comp.graphics',
 'comp.os.ms-windows.misc',
 'comp.sys.ibm.pc.hardware',
 'comp.sys.mac.hardware',
 'comp.windows.x',
 'rec.autos',
 'rec.motorcycles',
 'rec.sport.baseball',
 'rec.sport.hockey',
 'sci.crypt',
 'sci.electronics',
 'sci.med',
 'sci.space',
 'talk.politics.guns',
 'talk.politics.mideast',
 'talk.politics.misc']


collections = {
 'comp.graphics':"comp",
 'comp.os.ms-windows.misc':"comp",
 'comp.sys.ibm.pc.hardware':"comp",
 'comp.sys.mac.hardware':"comp",
 'comp.windows.x':"comp",
 'rec.autos':"rec",
 'rec.motorcycles':"rec",
 'rec.sport.baseball':"rec",
 'rec.sport.hockey':"rec",
 'sci.crypt':"sci",
 'sci.electronics':"sci",
 'sci.med':"sci",
 'sci.space':"sci",
 'talk.politics.guns':"politics",
 'talk.politics.mideast':"politics",
 'talk.politics.misc':"politics"} 

random_seed = 1983 
min_token_freq = 10
min_token_len = 2
max_token_len = 100
min_doc_length = 20 
max_doc_length = 800 
ds_name = "15Newsgroups"
data_dir = "D:\\data\\clda-data"
ds_dir = join(data_dir, ds_name)
raw_text_dir = join(ds_dir, "raw-texts")
dict_file = join(ds_dir, "%s.dict" % ds_name)
ldac_file = join(ds_dir, "%s.ldac" % ds_name)
tokens_file = join(ds_dir, "%s.tokens" % ds_name)
md_file = join(ds_dir, "%s.csv" % ds_name)
token_stats_file = join(ds_dir, "%s.token-stats" % ds_name)
if not exists(ds_dir): mkdir(ds_dir)
if not exists(raw_text_dir): mkdir(raw_text_dir)


# Custom stopwords 
stop_words += [u"ax", u"don", u"ll", u"ve", u"didn", u"etc"]


print "Loading 20 newsgroups dataset for categories:"
remove = ('headers', 'footers', 'quotes')  # ignores these 
ds = fetch_20newsgroups(subset='all', categories=categories, shuffle=True,
                        random_state=random_seed, remove=remove)
print 'data loaded'


def size_mb(docs): return sum(len(s.encode('utf-8')) for s in docs) / 1e6
print "%d documents - %0.3fMB" % (len(ds.data), size_mb(ds.data))
print "%d categories" % len(ds.target_names)
print 


doc_texts = []
doc_labels = []
doc_names = []
doc_collection = []
target_dict = dict(enumerate(ds.target_names))
for index, doc_text in enumerate(ds.data):
    doc_texts.append(doc_text)
    label = target_dict[ds.target[index]] # category 
    doc_labels.append(label)
    doc_collection.append(collections[label]) # collection 
    doc_names.append(ds.filenames[index])


    
###############################################################################
# Tokenizes text 
###############################################################################
print "Tokenizes text..."
import re

doc_tokens = []
token_stats = defaultdict(int)
for doc_text in doc_texts:
    doc_text = re.sub('\.\.+', ' ', doc_text) 
    doc_text = re.sub('\-\-+', '-', doc_text) 
    doc_text = re.sub('\_\_+', '_', doc_text) 
    tokens = re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[@.\w\-]+", 
                        doc_text)
    cleaned_tokens = []
    for w in tokens:
        try: 
            token = w.lower().strip().strip(STRIP_CHARS)  
            if not (token in stop_words  # removes stop words 
                    or is_date(token)  # discards dates   
                    or is_numeric(token)  # discards numeric values 
                    or len(token) < min_token_len
                    or max_token_len < len(token)): 
                cleaned_tokens.append(token)
                token_stats[token] += 1
        except: 
            pass  
    doc_tokens.append(cleaned_tokens)

print "DONE."

with codecs.open(token_stats_file, "w", encoding="utf-8") as tf: 
    print >> tf, "token,counts"
    for (k,v) in token_stats.items():
        print >> tf, "%s,%d" % (k, v)
        
        
###############################################################################    
# Creates the corpus dictionary
###############################################################################

dictionary = corpora.Dictionary(doc_tokens)        
filter_ids = [tid for tid, docfreq in dictionary.dfs.iteritems() 
              if (docfreq < (min_token_freq / 2))]
dictionary.filter_tokens(filter_ids) 
dictionary.compactify() 
vocab = dictionary.token2id.keys()

print dictionary



################################################################################
## Removes documents with word count < min_doc_length
################################################################################
num_docs = len(doc_tokens)
print "Number of documents:", num_docs
print "Deleting documents with size <", min_doc_length
i = 0
del_cnt = 0
while i < num_docs:
    doc_len = sum(1 for token in doc_tokens[i] if token in vocab)
    while ((doc_len < min_doc_length) or (doc_len > max_doc_length)) and (i < num_docs):
        print ".", 
        del doc_tokens[i]
        del doc_texts[i]
        del doc_labels[i]
        del doc_names[i]
        del doc_collection[i]
        num_docs -= 1
        del_cnt += 1        
        if i < num_docs:
            doc_len = sum(1 for token in doc_tokens[i] if token in vocab)
    i += 1
print "Number of documents deleted:", del_cnt
print "Number of remaining documents:", len(doc_tokens)

###############################################################################    
# Re-creates the corpus dictionary
###############################################################################

dictionary = corpora.Dictionary(doc_tokens)        
filter_ids = [tid for tid, docfreq in dictionary.dfs.iteritems() 
              if (docfreq < min_token_freq)]
dictionary.filter_tokens(filter_ids) 
dictionary.compactify() 
vocab = dictionary.token2id.keys()

print dictionary


###############################################################################    
# Saves data 
###############################################################################

print "Creates TF corpus"

tf_corpus = TFCorpusGenerator(dictionary, doc_tokens)
 
print "Stores the dictionary and corpus...",
 
dictionary.save(dict_file)
corpora.BleiCorpus.serialize(ldac_file, tf_corpus, id2word=dictionary)
 
print "DONE."
 
print "Saves metadata..."
 
with codecs.open(tokens_file, "w", encoding="utf-8") as pf, \
    codecs.open(md_file, "w", encoding="utf-8") as mf: 
    print >> mf, u'pageid,category,doclength,collection,name'   
    for i, doc_text in enumerate(doc_texts):
        raw_file = join(raw_text_dir, "%d.txt" % i)
        with codecs.open(raw_file, "w", encoding="utf-8") as fw:
            print >> fw, doc_text
        doc_t = [token for token in doc_tokens[i] if token in vocab]
        print >> pf, u' '.join(doc_t)
        print >> mf, u'%d,%s,%d,%s,%s' % (i, doc_labels[i], len(doc_t),
                                          doc_collection[i], doc_names[i])
        
print "DONE."



    


