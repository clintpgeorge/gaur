#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
This script tokenizes documents indexed in a file, normalizes tokens, creates 
a LDA-C formated corpus.   

Dependencies: 
    download_wikipedia_articles.py
    Python NLTK 
    Gensim (topic modeling toolkit)

Created By:          
    Clint P. George

Versions: 
    Created On:   Dec 14, 2013
    Modified On:  May 05, 2014   
    Modified On:  Feb 16, 2016. Removed PunktWordTokenizer as it was giving 
                                compiler errors 

'''

from build_ldac_corpus_wikipedia import * 


stop_words = load_en_stopwords('en_stopwords') 
print 'Number of stop words:', len(stop_words)


#===============================================================================
# To create LDA corpus based on the JSON input file created by 
# download_wikipedia_articles.py
#===============================================================================

# '''
# Added on Feb 27, 2014 
# '''
# 
# # If you wanna create topic modeling (LDA-c) corpus specifically for a set of 
# # categories, update them in the list category_filter 
# category_filter = ["Category:Baleen whales", 
#                     "Category:Dolphins", 
#                     "Category:Killer whales", 
#                     "Category:Oceanic dolphins", 
#                     "Category:Whale products", 
#                     "Category:Whaling"]
# dataset_name = 'Whales2'
# data_dir = 'E:\\Datasets\\%s' % dataset_name 
# 
# 
# pages_dir = join(data_dir, 'pages')
# page_info_file = join(data_dir, dataset_name + '.json') 
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
# build_ldac_corpus_json(page_info_file, pages_dir, 
#                        dict_file, ldac_file, 
#                        min_word_freq=15, 
#                        min_word_len=2, 
#                        max_word_len=20, 
#                        delimiter=";")
# 
#   
# '''
# Added on April 04, 2014 
# '''
#  
# category_filter = ["Category:Eagles", 
#                    "Category:Falcons", 
#                    "Category:Falco (genus)", 
#                    "Category:Falconry", 
#                    "Category:Harriers (birds)", 
#                    "Category:Hawks", 
#                    "Category:True_hawks", 
#                    "Category:Kites (birds)", 
#                    "Category:Owls"]
# dataset_name = 'Birds_of_prey'
# data_dir = 'E:\\Datasets\\%s' % dataset_name 
# pages_dir = join(data_dir, 'pages')
# page_info_file = join(data_dir, dataset_name + '.json') 
#      
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
#      
# build_ldac_corpus_json(page_info_file, pages_dir, 
#                        dict_file, ldac_file, 
#                        min_word_freq=15, 
#                        min_word_len=2, 
#                        max_word_len=20, 
#                        delimiter=";") 
#      
# '''
# Added on April 04, 2014 
# '''
# 
# category_filter = ["Category:Eagles", 
#                    "Category:Owls", 
#                    "Category:Ducks", 
#                    "Category:Ratites"]
# 
# dataset_name = 'Birds'
# data_dir = 'E:\\Datasets\\%s' % dataset_name 
# pages_dir = join(data_dir, 'intro')
# page_info_file = join(data_dir, dataset_name + '.json') 
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
#      
# build_ldac_corpus_json(page_info_file, pages_dir, dict_file, ldac_file, 
#                        min_word_freq = 5, min_word_len = 2, max_word_len = 20, 
#                        delimiter = ";", file_extension=".intro.text") 
# 
# 
#  
# '''
# Added on June 16, 2014 
# '''
#    
# dataset_name = 'Birds'
# data_dir = 'E:\\Datasets\\%s' % dataset_name 
# pages_dir = join(data_dir, 'pages')
# page_info_file = join(data_dir, dataset_name + '.json') 
# dict_file = join(data_dir, dataset_name + '-whole.dict') 
# ldac_file = join(data_dir, dataset_name + '-whole.ldac') 
# build_ldac_corpus_json(page_info_file, pages_dir, dict_file, ldac_file, 
#                   min_word_freq = 5, min_word_len = 2, max_word_len = 20, 
#                   delimiter = ";") 

 
'''
Added on August 05, 2015 
 
Wikipedia categories: Canis and Felines  
'''
################################################################################

# categories = ["Category:Jackals", "Category:Coyotes", "Category:Wolves"]
# dataset_name = "Canis"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# pages_dir = join(data_dir, 'pages')
#  
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 

# # Stept 1: 
# page_info_file = join(data_dir, dataset_name + '.json') 
# build_ldac_corpus_json(page_info_file, pages_dir, dict_file, ldac_file, 
#                   min_word_freq = 10, min_word_len = 2, max_word_len = 20, 
#                   delimiter = ",") 
# 
# # Step 2: This is to recreate corpus after manually checking the page index file
# # CSV file  
# page_info_file = join(data_dir, dataset_name + '2.csv') 
# build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, 
#                       min_word_freq=5, min_word_len=2, max_word_len=20, 
#                       delimiter=',')

################################################################################
# categories = ["Category:Acinonyx", "Category:Leopardus", "Category:Lynx", "Category:Prionailurus", "Category:Puma_(genus)"]
# dataset_name = "Felines"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# pages_dir = join(data_dir, 'pages')
#  
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
#  
# # Stept 1: 
# # page_info_file = join(data_dir, dataset_name + '.json') 
# # build_ldac_corpus_json(page_info_file, pages_dir, dict_file, ldac_file, 
# #                   min_word_freq = 10, min_word_len = 2, max_word_len = 20, 
# #                   delimiter = ";") 
#  
# # Step 2: This is to recreate corpus after manually checking the page index file
# # CSV file  
# page_info_file = join(data_dir, dataset_name + '2.csv') 
# build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, 
#                       min_word_freq=5, min_word_len=2, max_word_len=20, 
#                       delimiter=',')

################################################################################

# categories = ["Category:Leopardus", "Category:Lynx", "Category:Prionailurus"]
# dataset_name = "Cats"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# pages_dir = join(data_dir, 'pages')
#  
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
#  
# 
# # Step 2: This is to recreate corpus after manually checking the page index file
# # CSV file  
# page_info_file = join(data_dir, dataset_name + '.csv') 
# build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, 
#                       min_word_freq=7, min_word_len=2, max_word_len=20, 
#                       delimiter=',')
# 
# 
# categories = ["Category:Acinonyx", "Category:Leopardus", "Category:Prionailurus", "Category:Puma_(genus)"]
# dataset_name = "Felines"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# pages_dir = join(data_dir, 'pages')
#  
# dict_file = join(data_dir, dataset_name + '.dict') 
# ldac_file = join(data_dir, dataset_name + '.ldac') 
#  
# 
# # Step 2: This is to recreate corpus after manually checking the page index file
# # CSV file  
# page_info_file = join(data_dir, dataset_name + '.csv') 
# build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, 
#                       min_word_freq=5, min_word_len=2, max_word_len=20, 
#                       delimiter=',')



#===============================================================================
# Build corpus using a CSV file index 
# #===============================================================================
# '''
# To create LDA corpus based on the CSV file index  
#   
# Added on Dec 14, 2013  
# '''
#     
# data_folder = 'E:\\Datasets\\whales-tires-mixed2\\docs'  
# doc_path_index_file = 'E:\\Datasets\\whales-tires-mixed2\\whales-tires-mixed2.csv'
# dictionary_file = 'E:\\Datasets\\whales-tires-mixed2\\whales-tires-mixed2.dict' 
# ldac_file = 'E:\\Datasets\\whales-tires-mixed2\\whales-tires-mixed2.ldac'
#     
#   
# build_ldac_corpus2_csv(doc_path_index_file, data_folder, dictionary_file, ldac_file)

#dataset_name = 'whales-8p-intro'
#data_dir = 'E:\\Datasets\\%s' % dataset_name 
#pages_dir = join(data_dir, 'pages')
#page_info_file = join(data_dir, dataset_name + '.csv') 
#dict_file = join(data_dir, dataset_name + '.dict') 
#ldac_file = join(data_dir, dataset_name + '.ldac') 
#      
#build_ldac_corpus_csv3(page_info_file, pages_dir, dict_file, ldac_file, 
#                       min_word_freq = 2, min_word_len = 2, max_word_len = 100, 
#                       delimiter = ',') 
 
#  
# '''
# To create LDA corpus based on the CSV file index  
#    
# Added on Dec 14, 2013  
# '''
#  
# data_folder = 'E:\\Datasets\\wt8\\docs'  
# doc_path_index_file = 'E:\\Datasets\\wt8\\wt8.csv'
# dictionary_file = 'E:\\Datasets\\wt8\\wt8.dict' 
# ldac_file = 'E:\\Datasets\\wt8\\wt8.ldac'
# build_ldac_corpus2_csv(doc_path_index_file, data_folder, dictionary_file, 
#                        ldac_file, min_word_freq=2)
#  


#===============================================================================
# Added on April 04, 2014 
# Updated on December 05, 2015 
#===============================================================================

 
# category_filter = ["Category:Eagles", 
#                    "Category:Falco (genus)", 
#                    "Category:Harriers (birds)", 
#                    "Category:Hawks", 
#                    "Category:Kites (birds)", 
#                    "Category:Owls"]
# dataset_name = '6BirdsofPrey'

# category_filter = ["Category:Eagles", "Category:Falco (genus)"]
# dataset_name = 'eagles-falco'


# dataset_name = 'leopardus-puma'
dataset_name = 'eagles-owls'
data_dir = 'E:\\Datasets\\%s' % dataset_name 
pages_dir = join(data_dir, 'pages')
dict_file = join(data_dir, dataset_name + '.dict') 
ldac_file = join(data_dir, dataset_name + '.ldac') 
     
# # Step 1 
# page_info_file = join(data_dir, dataset_name + '.json') 
# build_ldac_corpus_json(page_info_file, pages_dir, 
#                        dict_file, ldac_file, 
#                        min_word_freq=10, 
#                        min_word_len=2, 
#                        max_word_len=20, 
#                        delimiter=";") 


# Step 2: This is to recreate corpus after manually checking the page index file
# CSV file  
page_info_file = join(data_dir, dataset_name + '.csv') 
build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, min_word_freq=5, 
                      min_word_len=2, max_word_len=20, delimiter=';')

