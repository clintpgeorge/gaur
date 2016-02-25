#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
This script tokenizes documents indexed in a file, normalizes tokens, creates 
a LDA-C formated corpus.   

Dependencies: 
    download_wikipedia_birds_01.py
    Python NLTK 
    Gensim (topic modeling toolkit)

Created By:          
    Clint P. George

Versions: 
    Created On:   Dec 14, 2013
    Modified On:  May 05, 2014   
    Modified On:  Feb 16, 2016 - updated for the dataset birds 

'''

from build_ldac_corpus_wikipedia import * 


dataset_name = 'birds'
data_dir = join('datasets', dataset_name) 
pages_dir = join(data_dir, 'pages')
dict_file = join(data_dir, dataset_name + '.dict') 
ldac_file = join(data_dir, dataset_name + '.ldac') 
     
# Step 1 
page_info_file = join(data_dir, dataset_name + '.json') 
build_ldac_corpus_json(page_info_file, 
                       pages_dir, 
                       dict_file, 
                       ldac_file, 
                       min_word_freq = 15, 
                       min_word_len = 2, 
                       max_word_len = 20, 
                       delimiter = ",") 




# # Step 2: This is to recreate corpus after manually checking the page index file
# # CSV file  
# page_info_file = join(data_dir, dataset_name + '.csv') 
# build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, min_word_freq=5, 
#                       min_word_len=2, max_word_len=20, delimiter=';')

