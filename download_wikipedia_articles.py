#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
This a test script to download the Wikipedia articles given a set of specified 
Wikipedia categories. 

Created on Feb 26, 2014

@author: Clint P. George 
'''

from utils_wikipedia import * 




#===============================================================================
# TEST SCRIPTS 
#===============================================================================

cats = [    {'title':'Category:Birds of prey', 'category-path':'', 'collection':'Birds of prey'}, 
            {'title':'Category:Hummingbirds', 'category-path':'', 'collection':'Hummingbirds'}, 
            {'title':'Category:Parrots', 'category-path':'', 'collection':'Parrots'}, 
            {'title':'Category:Perching_birds', 'category-path':'', 'collection':'Perching_birds'}, 
            {'title':'Category:Seabirds', 'category-path':'', 'collection':'Seabirds'}]
pages = get_collection_page_urls(cats, [], recurse = True)


        
        
dataset_name = "birds"
data_dir = os.path.join("datasets", dataset_name) # the download directory 
pages_dir = os.path.join(data_dir, 'pages')
page_info_file = os.path.join(data_dir, dataset_name) 
 
if not os.path.exists(pages_dir):
    os.makedirs(pages_dir)
    
with open(os.path.join(data_dir, "%s.text" % dataset_name), "w") as fw:
    for page in pages: 
        print >>fw, page 

start_time = datetime.now()
 
count = download_wikipages(page_info_file, pages_dir, pages)

print 
print count, 'articles are downloaded.'
print 'Execution time:', (datetime.now() - start_time)



# categories = ["Category:Heart_diseases"] # Specify the Wikipedia categories 
# dataset_name = 'Heart_diseases' # the data-set name 
 
# categories = ["Category:Whales", "Category:Killer whales", 
#               "Category:Baleen whales", "Category:Toothed whales"]
# dataset_name = 'Whales-6'

# categories = ["Category:Birds_by_common_name"] 
# dataset_name = 'Birds_by_common_name'

# categories = ["Category:Eagles", "Category:Falcons", 
#               "Category:Harriers (birds)", "Category:Hawks", 
#               "Category:Kites (birds)", "Category:Owls"]
# dataset_name = "Birds_of_prey"

 
# categories = ["Category:Eagles", "Category:Falcons", 
#               "Category:Harriers (birds)", "Category:Hawks", 
#               "Category:Kites (birds)", "Category:Owls", 
#               "Category:Ducks", "Category:Swans", "Category:Ratites"]
# dataset_name = "Birds"
#      


# categories = ["Category:Eagles", "Category:Falco_(genus)", 
#               "Category:Harriers (birds)", "Category:Hawks", 
#               "Category:Kites (birds)", "Category:Owls"]
# dataset_name = "6BirdsofPrey"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# download_and_save(categories, dataset_name, data_dir)

# # Added on December 05, 2015 
# categories = ["Category:Jackals", "Category:Wolves"]
# dataset_name = "jackals-wolves"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# download_and_save(categories, dataset_name, data_dir)

# # Added on December 05, 2015 
# categories = ["Category:Eagles", "Category:Falco_(genus)"]
# dataset_name = "eagles-falco"
# data_dir = "datasets/%s" % dataset_name # the download directory 
# download_and_save(categories, dataset_name, data_dir)

# # Added on December 05, 2015 
# categories = ["Category:Ducks", "Category:Swans"]
# dataset_name = "ducks-swan"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# download_and_save(categories, dataset_name, data_dir)

# 
# categories = ["Category:Animals"]
# dataset_name = "Animals"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# 
# download_and_save(categories, dataset_name, data_dir)


# ################################################################################
# ## Run date: August 05, 2015 
# ################################################################################
# categories = ["Category:Jackals", "Category:Coyotes", "Category:Wolves"]
# dataset_name = "Canis"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# 
# download_and_save(categories, dataset_name, data_dir)


# ################################################################################
# ## Run date: August 05, 2015 
# ################################################################################
# categories = ["Category:Acinonyx", "Category:Leopardus", "Category:Lynx", "Category:Prionailurus", "Category:Puma_(genus)"]
# dataset_name = "Felines"
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# 
# download_and_save(categories, dataset_name, data_dir)

