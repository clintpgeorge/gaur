# -*- coding: utf-8 -*-
"""Compares the LDA Augmented Collapsed Gibbs sampling algorithm implementation 
with the gensim LDA implementation (based on the online variational inference)
using a dataset created from a subset of the Wikipedia articles.
 
Created on Sat Feb 25 2015

@author: Clint P. George 
"""

import gensim 
import cProfile, pstats, StringIO

from time import time
from lda_gibbs import AugmentedCollapsedGibbsSampler, print_topics
from os.path import join 

###############################################################################
# Loads the Wikipedia dataset 
###############################################################################

num_topics = 2
#alpha = 1. / num_topics
#eta = 1. / num_topics
alpha = 50. / num_topics
eta = .1
max_iter = 1000
burn_in_iter = 999
random_seed = 1983 

data_dir = "datasets"
project_name = "whales-tires"

# loads the corpus 

dict_file = join(data_dir, project_name + '.dict')
ldac_file = join(data_dir, project_name + '.ldac')  
vocab_file = join(data_dir, project_name + '.ldac.vocab')  
corpus = gensim.corpora.BleiCorpus(ldac_file)
id2word = gensim.corpora.Dictionary().load(dict_file)
vocab_size = len(id2word)  

        

###############################################################################
# ACGS
###############################################################################
print "LDA ACGS:"
acgs = AugmentedCollapsedGibbsSampler(corpus, num_topics, vocab_size, 
                                      alpha, eta, max_iter, max_iter-1, 
                                      store_beta=True, store_theta=True, 
                                      store_z=False, 
                                      random_seed=random_seed)
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
print "LDA Online VB (Gensim):"
t0 = time()
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, 
                                      id2word=id2word, 
                                      num_topics=num_topics, update_every=1, 
                                      passes=50, alpha=alpha, eta=eta)
m, s = divmod((time() - t0), 60)
h, m = divmod(m, 60)
print "Execution time: %d:%02d:%02d" % (h, m, s)                                      
print "-"*100

###############################################################################
# Print inferred topics 
###############################################################################

id2word = dict(id2word.items())
print "Gensim:"
print_topics(lda.expElogbeta, id2word)
print 
print "ACGS:"
print_topics(acgs.Beta[0], id2word)
print 