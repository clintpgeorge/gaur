# -*- coding: utf-8 -*-
"""Compares the LDA Augmented Collapsed Gibbs sampling algorithm implementation 
with the gensim LDA implementation (based on the online variational inference).
 
Created on Sat Feb 21 13:49:51 2015

@author: Clint P. George 
"""

import gensim 
import cProfile, pstats, StringIO

from gensim import corpora
from time import time
from lda_gibbs import AugmentedCollapsedGibbsSampler, print_topics


###############################################################################
# Creating the toy dataset 
###############################################################################
documents = ["Human machine interface for lab abc computer applications",
             "A survey of user opinion of computer system response time",
             "The EPS user interface management system",
             "System and human system engineering testing of EPS",
             "Relation of user perceived response time to error measurement",
             "The generation of random binary unordered trees",
             "The intersection graph of paths in trees",
             "Graph minors IV Widths of trees and well quasi ordering",
             "Graph minors A survey", 
             "a and"]
stoplist = set('for a of the and to in'.split())
texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in documents]

# remove words that appear only once
all_tokens = sum(texts, [])
tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
texts = [[word for word in text if word not in tokens_once]
         for text in texts]

#print(texts)

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]


###############################################################################
# ACGS
###############################################################################

num_topics = 2
vocab_size = len(dictionary)  
alpha = 1
eta = 1
max_iter = 1000
burn_in_iter = 999
print "-"*100
acgs = AugmentedCollapsedGibbsSampler(corpus, num_topics, vocab_size, alpha, 
                                      eta, max_iter, burn_in_iter, 
                                      store_beta=True, store_theta=True, 
                                      store_z=True, random_seed=1983)

pr = cProfile.Profile()
t0 = time()
pr.enable()
acgs.fit()
pr.disable()
m, s = divmod((time() - t0), 60.)
h, m = divmod(m, 60.)
print "Execution time: %d:%02d:%02d" % (h, m, s)
s = StringIO.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats()
print "-"*100
print s.getvalue()
print "-"*100      

###############################################################################
# Gensim LDA 
###############################################################################
print "Gensim LDA:"
t0 = time()
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, 
                                      id2word=dictionary, 
                                      num_topics=num_topics, update_every=1, 
                                      passes=50, alpha=alpha, eta=eta)
m, s = divmod((time() - t0), 60)
h, m = divmod(m, 60)
print "Execution time: %d:%02d:%02d" % (h, m, s)                                      
print "-"*100

id2token = dict(dictionary.items())
print_topics(lda.expElogbeta, id2token)
print_topics(acgs.Beta[0], id2token)