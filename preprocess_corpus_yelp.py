'''

Versions:
    Jul 05, 2016 - Created 



@author: Clint P. George
'''

import codecs 
import glob

from os.path import join, basename, splitext
from collections import defaultdict

data_dir = "D:\\data\\clda-data\\yelp"
review_dir_name = "reviews"
ds_name = "yelp"
metadata_file_path = join(data_dir, "%s-raw.csv" % ds_name)  
categories_file_path = join(data_dir, "%s-cat.csv" % ds_name) 
ratings_file_path = join(data_dir, "%s-rat.csv" % ds_name) 
review_dir = join(data_dir, review_dir_name)  

review_file_paths = glob.glob(join(review_dir, "*.txt"))



categories_dict = defaultdict(int)
ratings_dict = defaultdict(int)

with codecs.open(metadata_file_path, "w", encoding="utf-8") as mf: 
    # metadata header 
    print >> mf, "review-id,reviewer-id,rating,restaurant,category,row-word-count"   

    for file_path in review_file_paths:
        # print file_path 
        
        with codecs.open(file_path, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            review_id = basename(file_path).rstrip(".txt") # lines[0].lstrip("ReviewID:").strip() 
            reviewer_id = lines[1].lstrip("ReviewerID:").strip() 
            rating = lines[2].lstrip("Rating:").strip()
            restaurant = lines[3].lstrip("Restaurant:").strip()
            category = lines[4].lstrip("Category:").strip()
            categories_dict[category] += 1
            ratings_dict[rating] += 1
            row_word_count = len((" ".join(lines[5:])).split())
            print >> mf, "%s,%s,%s,%s,%s,%d" % (review_id, reviewer_id, rating, 
                                                restaurant, category, 
                                                row_word_count)  
            
            
with codecs.open(categories_file_path, "w", encoding="utf-8") as mf: 
    # metadata header 
    print >> mf, "category,count"  
    for k, v in categories_dict.items():
        print >> mf, "%s,%d" % (k, v) 
         
with codecs.open(ratings_file_path, "w", encoding="utf-8") as mf: 
    # metadata header 
    print >> mf, "rating,count"  
    for k, v in ratings_dict.items():
        print >> mf, "%s,%d" % (k, v)  
        
      
