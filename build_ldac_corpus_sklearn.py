# -*- coding: utf-8 -*-
"""This script creates datsets to evaluate the method for selecting 
hyperparameters for the LDA model   


Created on Sun Mar 01 20:50:00 2015

@author: Clint P. George 
"""


import codecs 
from random import shuffle, seed
from os.path import exists, join
from os import mkdir
from collections import defaultdict 
from sklearn.datasets import fetch_20newsgroups
from gensim import corpora
from utils_text import regex_tokenizer


def sample_20newsgroups_docs(categories, sample_size = 50, 
                             doc_len_range = (200, 600), random_seed = 1983):
    """Creates a subset of documents and their labels from the 20newsgroups 
    dataset given in the sklearn.datasets package. 
    
    Arguments: 
        categories - subset of selected categories 
        sample_size - number of documents in a categories  
        doc_len_range - document length range 
        random_seed - seed for random number generation 
    """
    
    print "Loading 20 newsgroups dataset for categories:"
    remove = ('headers', 'footers', 'quotes') # ignores these 
    ds = fetch_20newsgroups(subset='all', categories=categories, shuffle=True, 
                              random_state=random_seed, remove=remove)
    print 'data loaded'
    
    
    def size_mb(docs): return sum(len(s.encode('utf-8')) for s in docs) / 1e6
    print "%d documents - %0.3fMB" % (len(ds.data), size_mb(ds.data))
    print "%d categories" % len(ds.target_names)
    print 

    len_start, len_end = doc_len_range
    doc_lengths = [len(doc.split()) for doc in ds.data]
    doc_indices = [index for index, dl in enumerate(doc_lengths) 
                   if (dl > len_start and dl < len_end)]
    cat_doc_indices = defaultdict(list)
    for doc_index in doc_indices:
        cat_id = ds.target[doc_index]
        cat_doc_indices[cat_id] += [doc_index]
        
    selected_doc_indices = []
    for cat_id, indices in cat_doc_indices.items():
        assert(len(indices) > sample_size)
        for i in xrange(sample_size):
            selected_doc_indices.append(indices[i])
    seed(random_seed)
    shuffle(selected_doc_indices)
    
    
    doc_texts = []
    doc_labels = []
    doc_names = []
    target_dict = dict(enumerate(ds.target_names))
    
    for index in selected_doc_indices:
        doc_texts.append(ds.data[index])
        doc_labels.append(target_dict[ds.target[index]])
        doc_names.append(ds.filenames[index])
        
    return (doc_texts, doc_labels, doc_names)



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



def build_gensim_dictionary(doc_tokens, min_token_freq, min_token_len, 
                            max_token_len):
    """Builds the gensim corpus dictionary
    
    """
    
    # collect statistics about all tokens
    dictionary = corpora.Dictionary(doc_tokens)        
    # filter words 
    filter_ids = [tid for tid, docfreq in dictionary.dfs.iteritems() 
                  if (docfreq < min_token_freq 
                      or len(dictionary[tid]) < min_token_len 
                      or len(dictionary[tid]) > max_token_len)]
    dictionary.filter_tokens(filter_ids) 
    # remove gaps in id sequence after words that were removed
    dictionary.compactify() 

    return dictionary



###############################################################################
# Program main flow 
# 20newsgroups
# http://scikit-learn.org/stable/datasets/twenty_newsgroups.html
# http://kdd.ics.uci.edu/databases/20newsgroups/20newsgroups.data.html


###############################################################################
## Hard coded values. Should be edited/checked before running this script  
###############################################################################

data_dir = "D:\\datasets\\20newsgroups"
min_token_len = 2 
max_token_len = 100


sample_size = 50
min_token_freq = 5

## C-5a
#ds_name = "med-christian-baseball"
#categories = [  
#                'sci.med',
#                'soc.religion.christian',
#                'rec.sport.baseball'
#             ]
#             
## C-6
#ds_name = "rec"
#categories = [  
#                'rec.autos',
#                'rec.motorcycles',
#                'rec.sport.baseball',
#                'rec.sport.hockey',
#             ]
## C-7
#ds_name = "sci"
#categories = [  
#                'sci.crypt',
#                'sci.electronics',
#                'sci.med',
#                'sci.space',
#             ]  
#
## C-8
#ds_name = "christian-atheism-religion"
#categories = [  
#                'soc.religion.christian',
#                'alt.atheism',
#                'talk.religion.misc'
#             ]            

## C-5b
#ds_name = "med-christian-baseball-30D"
#categories = [  
#                'sci.med',
#                'soc.religion.christian',
#                'rec.sport.baseball'
#             ]
#sample_size = 10
#min_token_freq = 2

# C-9
ds_name = "ibm-mac"
categories = [  
                'comp.sys.ibm.pc.hardware',
                'comp.sys.mac.hardware',
             ]  

###############################################################################
# Gets data from sklearn 
###############################################################################

doc_texts, doc_labels, doc_names = sample_20newsgroups_docs(categories, 
                                                            sample_size)



###############################################################################
# Tokenizes text 
###############################################################################

doc_tokens = [regex_tokenizer(doc_text) for doc_text in doc_texts]



###############################################################################    
# Creates the corpus dictionary, LDA-c formatted file, and the vocabulary file  
###############################################################################
gensim_dict = build_gensim_dictionary(doc_tokens, min_token_freq, min_token_len, 
                                      max_token_len)
tf_corpus = TFCorpusGenerator(gensim_dict, doc_tokens)



###############################################################################    
# Saves data 
###############################################################################

ds_dir = join(data_dir, ds_name)
raw_text_dir = join(ds_dir, "raw-texts")
dict_file = join(ds_dir, "%s.dict" % ds_name)
ldac_file = join(ds_dir, "%s.ldac" % ds_name)
tokens_file = join(ds_dir, "%s.tokens" % ds_name)
md_file = join(ds_dir, "%s.csv" % ds_name)

if not exists(ds_dir): mkdir(ds_dir)
if not exists(raw_text_dir): mkdir(raw_text_dir)
    
    
# Stores the dictionary and corpus, for future reference
gensim_dict.save(dict_file)
corpora.BleiCorpus.serialize(ldac_file, tf_corpus, id2word=gensim_dict)
vocab = gensim_dict.token2id.keys()

with codecs.open(tokens_file, "w", encoding="utf-8") as pf, \
    codecs.open(md_file, "w", encoding="utf-8") as mf: 
    print >>mf, u'pageid;category;doclength'   
    for i, doc_text in enumerate(doc_texts):
        raw_file = join(raw_text_dir, "%d.txt" % i)
        with codecs.open(raw_file, "w", encoding="utf-8") as fw:
            print >>fw, doc_text
        doc_t = [token for token in doc_tokens[i] if token in vocab]
        print >>pf, u' '.join(doc_t)
        print >>mf, u'%d;%s;%d' % (i, doc_labels[i], len(doc_t))

