#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
This a test script to download the Wikipedia articles given a set of specified 
Wikipedia categories. 

Created on  Feb 26, 2014
Modified on Feb 16, 2016 

@author: Clint P. George 
'''

from utils_wikipedia import * 




#===============================================================================
# TEST SCRIPTS 
#===============================================================================

cats = [    {'title':'Category:Hummingbirds', 'category-path':'', 'collection':'Hummingbirds'}, 
            {'title':'Category:Parrots', 'category-path':'', 'collection':'Parrots'}
            ]
 
dataset_name = "hummingbirds-parrots"
data_dir = os.path.join("datasets", dataset_name) # the download directory 
pages_dir = os.path.join(data_dir, 'pages')
page_info_file = os.path.join(data_dir, dataset_name) 
  
if not os.path.exists(pages_dir):
    os.makedirs(pages_dir)
     
pages = get_collection_page_urls(cats, [], [], recurse = True)
     
with open(os.path.join(data_dir, "%s.text" % dataset_name), "w") as fw:
    for page in pages: 
        print >>fw, page
        
print 'Number of page urls:', len(pages)
 
start_time = datetime.now()
  
count = download_wikipages(page_info_file, pages_dir, pages)
 
print 
print count, 'articles are downloaded.'
print 'Execution time:', (datetime.now() - start_time)


