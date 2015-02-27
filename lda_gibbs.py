# -*- coding: utf-8 -*-
"""
Versions:
    * Created on Fri Feb 20 12:33:32 2015

@author: Clint P. George
"""
from numpy import zeros, argsort, array
from numpy.random import seed, dirichlet, random#, multinomial, randint

   
def print_topics(beta, id2token, topn=20):
    num_topics, vocab_size = beta.shape
    col_names = [id2token[i] for i in xrange(vocab_size)]
    for k in xrange(num_topics):
        topic_row = beta[k, :]
        sorted_index = argsort(topic_row)[::-1][1:topn]
        print ", ".join("%s(%.2f)" % (col_names[sidx], topic_row[sidx]*100.) for sidx in sorted_index)
        

class AugmentedCollapsedGibbsSampler():
    
    def __init__(self, corpus, num_topics, vocab_size, alpha, eta, 
                 max_iter, burn_in_iter, spacing=1, store_beta=False, 
                 store_theta=False, store_z=False, random_seed=1983):
        """
        AugmentedCollapsedGibbsSampler 
        ------------------------------
        
        This implementation assumes symmetric Dirichlets for the LDA priors.  
          
        """
        
        self.num_topics = num_topics
        self.vocab_size = vocab_size
        self.alpha = float(alpha)
        self.eta = float(eta)
        self.max_iter = max_iter
        self.burn_in_iter = burn_in_iter
        self.spacing = spacing
        self.store_beta = store_beta
        self.store_theta = store_theta
        self.store_z = store_z
        self.random_seed = random_seed
        self.Z = []
        self.Theta = []
        self.Beta = []        
        
        assert(self.num_topics > 1)
        assert(self.vocab_size > 1)
        assert(self.alpha > 0.)
        assert(self.eta > 0.)
        assert(self.max_iter > 1)
        assert(self.max_iter > self.burn_in_iter)
        
        #######################################################################
        # Process data
        #######################################################################
        
        self.word_ids = []
        self.doc_ids = []
        self.doc_lengths = []  
        self.doc_word_indices = []  
        self.num_corpus_words = 0
        self.num_docs = 0              
        
        # Gets the document index for each word instance
        # Gets the indices of words in a document as a vector
        for doc in corpus:
            word_indices = []
            doc_length = 0
            for word_id, word_count in doc:
                for _ in xrange(int(word_count)):                
                    self.word_ids.append(word_id) # word instance 
                    self.doc_ids.append(self.num_docs) # document instance 
                    word_indices.append(self.num_corpus_words)
                    self.num_corpus_words += 1 # increment the number of words
                    doc_length += 1
            self.doc_lengths.append(doc_length)
            self.doc_word_indices.append(word_indices)
            self.num_docs += 1 # increment the number of docs 
            
        #######################################################################


        
    def draw_multinomial(self, pvals, pvals_sum=1.):
        """Draw a sample from a multinomial distribution and return the index of 1.
    
        The multinomial distribution is a multivariate generalisation of the 
        binomial distribution. Take an experiment with one of p possible outcomes. 
        An example of such an experiment is throwing a dice, where the outcome can 
        be 1 through 6. Each sample drawn from the distribution represents n such 
        experiments. Its values, X_i = [X_0, X_1, ..., X_p], represent the number 
        of times the outcome was i.
        
        Parameters
    
        pvals       : Sequence of floats, length p. Probabilities of each of the p 
                      different outcomes. 
        pvals_sum   : sum(pvals_sum), default 1. (It means pvals sums to 1.) 
        
        """
        
        index = 0
        u = random() * pvals_sum
        cumulative_prob = pvals[0]
        while u > cumulative_prob:
            index += 1
            cumulative_prob += pvals[index]    
        return index  

    def initialize_state(self):
        """Initializes z, beta, theta, and topic counts 
        """
        
        # Sets seed 
        seed(seed=self.random_seed)  

        # Return random integers from the “discrete uniform” distribution in 
        # the “half-open” interval [low, high).
        # self.z = randint(low=0, high=self.num_topics, size=self.num_corpus_words) 
        
        pvals = zeros(self.num_topics) # multinomial prob. vector 
        pvals.fill(self.alpha)
        pvals /= pvals.sum() # makes it sums to 1. 
        self.z = zeros(self.num_corpus_words)         
        
        self.beta_counts = zeros((self.num_topics, self.vocab_size))
        self.beta_counts.fill(self.eta)
        
        self.theta_counts = zeros((self.num_topics, self.num_docs))
        self.theta_counts.fill(self.alpha)
        self.topic_counts = zeros(self.num_topics)
        
        for i in xrange(self.num_corpus_words):
            tid = self.draw_multinomial(pvals)
            self.z[i] = tid
            self.beta_counts[tid, self.word_ids[i]] += 1.
            self.topic_counts[tid] += 1.
            self.theta_counts[tid, self.doc_ids[i]] += 1.

            
        

    def fit(self, message_interval=100):

        # Initializes z, beta, theta, and topic counts 
        
        self.initialize_state()
        
        # Gibbs sampling 
        
        if message_interval >= self.max_iter: 
            message_interval = 1
            
        print "Number of documents: %d" % self.num_docs
        print "Number of words in the corpus: %d" % self.num_corpus_words 
        print "Maximum number of Gibbs iterations: %d" % self.max_iter
        print "Burn in period: %d" % self.burn_in_iter
        print "Message interval: %d" % message_interval
        print "Gibbs sampling" #,
        print "-"*100
        
        # Identifying the constants for the iterations 
        # This is to speed up 
        doc_denom = (array(self.doc_lengths) - 1. + self.num_topics * self.alpha) # a constant for k
        vocab_size_x_eta = self.vocab_size * self.eta
        
        for iteration in xrange(self.max_iter):
            
            if (iteration + 1) % message_interval == 0: 
                print "lda_acgs: gibbs iter #%d" % (iteration + 1) # ".", # 
            
            store_flg = (iteration >= self.burn_in_iter 
                         and iteration % self.spacing == 0)
            
            # Saves augmented beta samples  
            
            if store_flg and self.store_beta:
                beta = zeros((self.num_topics, self.vocab_size))                    
                for k in xrange(self.num_topics):                    
                    beta[k,:] = dirichlet(self.beta_counts[k,:], 1)
                self.Beta.append(beta)
            
            # Saves augmented theta samples 
            
            if store_flg and self.store_theta:
                theta = zeros((self.num_topics, self.num_docs))
                for d in xrange(self.num_docs):                    
                    theta[:,d] = dirichlet(self.theta_counts[:,d], 1)
                self.Theta.append(theta) 
            
            for i in xrange(self.num_corpus_words): # for each word instance 
                wid = self.word_ids[i] # word index 
                did = self.doc_ids[i] # document index 
                tid = self.z[i] # current topic 
                
                
                # decrements the counts by 1
                
                self.beta_counts[tid, wid] -= 1. 
                self.theta_counts[tid, did] -= 1. 
                self.topic_counts[tid] -= 1.
                
                # computes pvals 

                # pvals = zeros(self.num_topics) # multinomial prob. vector 
                # Note: I found that using numpy data strutures slows down 
                #       execution. That's why the below lines are commented 
                #       and followed a pure python approach (See below). 
                #       The analysis is performed based on the python package 
                #       cProfile, pstats, etc. 
                # pvals = zeros(self.num_topics)              
                # for k in xrange(self.num_topics):
                #     pvals[k] = ((self.theta_counts[k, did] / doc_denom[did]) 
                #                 * (self.beta_counts[k, wid]  
                #                   / (self.topic_counts[k] + vocab_size_x_eta)))

                pvals = []                
                pvals_sum = 0.
                for k in xrange(self.num_topics):
                    pval = ((self.theta_counts[k, did] / doc_denom[did]) 
                            * (self.beta_counts[k, wid]  
                              / (self.topic_counts[k] + vocab_size_x_eta)))
                    pvals.append(pval)
                    pvals_sum += pval

                # Multinomial sampling 

                # Note: multinomial requires the vector pvals to sums to 1. 
                #       If we are using draw_multinomial it's not required.
                #       In addition, we found that the numpy multinomial 
                #       is slower than draw_multinomial   
                # tid =  multinomial(1, pvals/pvals_sum, size=1).argmax()  
                tid = self.draw_multinomial(pvals, pvals_sum)
                
                # increments the counts by 1 

                self.beta_counts[tid, wid] += 1.
                self.theta_counts[tid, did] += 1.
                self.topic_counts[tid] += 1.                
                self.z[i] = tid
                
            # Saves z samples 
            if store_flg and self.store_z: 
                self.Z.append(self.z)

                   
        print "-"*100
        print "Number of saved z samples: %d" % len(self.Z)
        print "Number of saved beta samples: %d" % len(self.Beta)
        print "Number of saved theta samples: %d" % len(self.Theta)



