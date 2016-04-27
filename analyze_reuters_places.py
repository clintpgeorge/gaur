'''
Created on Apr 8, 2016

@author: clintpg
'''

import codecs
from os.path import join 
from collections import defaultdict

data_dir = "D:\\data\\clda-data"
ds_name = "reuters-21578"
# loc_country_file_path = join(data_dir, "%s.countries" % ds_name) 
md_file_path = join(data_dir, "%s.csv" % ds_name) 

europe = "albania andorra austria  belgium  bulgaria  denmark  east-germany  west-germany  finland  france  greece  hungary  ireland  italy  netherlands  norway poland portugal romania spain sweden  switzerland uk vatican"
asia = "afghanistan  russia  bahrain  bangladesh  burma  china  hong-kong  india  indonesia  iran  iraq  israel  kuwait  malaysia north-korea oman pakistan  qatar saudi-arabia singapore south-korea sri-lanka syria thailand ussr vietnam japan philippines"
us = "american-samoa  usa  canada"

europe = [w.strip() for w in europe.split()]
asia = [w.strip() for w in asia.split()]
us = [w.strip() for w in us.split()]

def contains(tags, places):
    for tag in tags:
        if tag in places: 
            return True
    return False   


country_stats = defaultdict(int)

with codecs.open(md_file_path, "r", encoding="utf-8") as mf:  
    line_count = 0
    for line in mf:
        if line_count == 0: 
            line_count += 1
            continue
        elements = line.strip().split(",")
        places = elements[2].split()
        
        if contains(europe, places):
            country_stats["europe"] += 1
        elif contains(asia, places):
            country_stats["asia"] += 1
        elif elements[2].strip() == "usa" or elements[2].strip() == "canada" or elements[2].strip() == "american-samoa": 
            country_stats["us"] += 1
        else: 
            country_stats["rest"] += 1
        line_count += 1
        
print "Number of entries:", line_count

for k,v in country_stats.items():
    print k, v 



# country_stats = defaultdict(int)
# 
# with codecs.open(loc_country_file_path, "r", encoding="utf-8") as cf:  
#     line_count = 0
#     for line in cf:
#         if line_count == 0: 
#             line_count += 1
#             continue
#         place, count, country = line.strip().split(",")
#         
#         country = country.split("|")[0] # take the first item 
#         country_stats[country] += 1
#         line_count += 1
#         
# print "Number of entries:", line_count
# 
# for k,v in country_stats.items():
#     print k, v 