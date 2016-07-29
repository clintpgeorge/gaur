'''

Versions:
    April 18, 2016 - Original version 
    June 16, 2016  - Processing the whole NIPS 1-17 dataset 
    July 05, 2016  - Customizing for the Yelp dataset  

References: 
    http://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    http://www.nltk.org/howto/corpus.html

@author: Clint P. George 
'''
import codecs 
import re
import glob
from os.path import join, basename
from collections import defaultdict
from gensim import corpora
from utils_text import stop_words, is_date, is_numeric, STRIP_CHARS

pattern = re.compile('[\W_]+')

def custom_tokenizer(doc_text, max_token_len):
    doc_text = re.sub('\.\.+', ' ', doc_text) 
    doc_text = re.sub('\-\-+', '-', doc_text) 
    doc_text = re.sub('\_\_+', '_', doc_text) 
    tokens = re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[@.\w\-]+", 
                        doc_text)
    cleaned_tokens = []
    for w in tokens:
        try: 
            token = w.lower().strip().strip(STRIP_CHARS)  
            if not (token in stop_words  # removes stop words 
                    or is_date(token)  # discards dates   
                    or is_numeric(token)  # discards numeric values 
                    or (len(token) < 2) 
                    or max_token_len < len(token)): 
                cleaned_tokens.append(token)
        except: 
            pass  
        
    return cleaned_tokens



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


 
data_dir = "D:\\data\\clda-data\\yelp"
review_dir_name = "reviews"
ds_name = "yelp"
metadata_file_path = join(data_dir, "%s-raw.csv" % ds_name)  

review_dir = join(data_dir, review_dir_name)  
categories_file_path = join(data_dir, "%s-cat.csv" % ds_name) 
ratings_file_path = join(data_dir, "%s-rat.csv" % ds_name) 
review_dir = join(data_dir, review_dir_name)  

review_file_paths = glob.glob(join(review_dir, "*.txt"))


ignore_categories = ["Performing Arts", "Gay Bars", "Nightlife", 
                     "Venues & Event Spaces"]

min_token_freq = 10
max_token_len = 100
min_doc_length = 40
max_doc_length = 800

# Custom stopwords 
stop_words += [u"ax", u"don", u"ll", u"ve", u"didn", u"etc"]

metadata_file_path = join(data_dir, "%s-raw.csv" % ds_name)  
token_stats_file = join(data_dir, "%s.token-stats" % ds_name)
dict_file = join(data_dir, "%s.dict" % ds_name)
ldac_file = join(data_dir, "%s.ldac" % ds_name)
tokens_file = join(data_dir, "%s.tokens" % ds_name)
md_file = join(data_dir, "%s.csv" % ds_name)

token_stats = defaultdict(int)
doc_ids = []
review_ids = []
reviewer_ids = []
doc_raw_wc = []
doc_tokens = []
ratings = []
categories = []
restaurants = []
num_articles = 0 






categories_dict = defaultdict(int)
ratings_dict = defaultdict(int)

with codecs.open(metadata_file_path, "w", encoding="utf-8") as mf: 
    # metadata header 
    print >> mf, "doc-id,review-id,reviewer-id,rating,restaurant,category,row-word-count"   

    for file_path in review_file_paths:
        # print file_path 
        
        with codecs.open(file_path, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            review_id = basename(file_path).rstrip(".txt") # lines[0].lstrip("ReviewID:").strip() 
            reviewer_id = lines[1].lstrip("ReviewerID:").strip() 
            rating = lines[2].lstrip("Rating:").strip()
            restaurant = lines[3].lstrip("Restaurant:").strip()
            category = lines[4].lstrip("Category:").strip()
            
            if category in ignore_categories:
                continue
            
            categories_dict[category] += 1
            ratings_dict[rating] += 1

            article_text = " ".join(lines[5:])
            tokens = custom_tokenizer(article_text, max_token_len)
            for token in tokens: 
                token_stats[token] += 1

            raw_word_count = len(article_text.split())
            
            if raw_word_count < min_doc_length:
                continue
            
            num_articles += 1
            
            print >> mf, "%d,%s,%s,%s,%s,%s,%d" % (num_articles, review_id, 
                                                   reviewer_id, rating, 
                                                   restaurant, category, 
                                                   raw_word_count)  
            doc_ids.append(num_articles)
            doc_raw_wc.append(raw_word_count)
            doc_tokens.append(tokens)
            ratings.append(rating)
            categories.append(category)
            review_ids.append(review_id)
            reviewer_ids.append(reviewer_id)
            restaurants.append(restaurant)


            
     
print "Total number of articles:", num_articles

with codecs.open(token_stats_file, "w", encoding="utf-8") as tf: 
    print >> tf, "token,counts"
    for (k,v) in token_stats.items():
        print >> tf, "%s,%d" % (k, v)
        
        
###############################################################################    
# Creates the corpus dictionary
###############################################################################

dictionary = corpora.Dictionary(doc_tokens)        
filter_ids = [tid for tid, docfreq in dictionary.dfs.iteritems() 
              if (docfreq < min_token_freq)]
dictionary.filter_tokens(filter_ids) 
dictionary.compactify() 
vocab = dictionary.token2id.keys()

print dictionary


###############################################################################    
# Saves data 
###############################################################################

print "Creates TF corpus"

tf_corpus = TFCorpusGenerator(dictionary, doc_tokens)
 
print "Stores the dictionary and corpus...",
 
dictionary.save(dict_file)
corpora.BleiCorpus.serialize(ldac_file, tf_corpus, id2word=dictionary)
 
print "DONE."
 
print "Saves metadata..."
 
with codecs.open(tokens_file, "w", encoding="utf-8") as pf, \
    codecs.open(md_file, "w", encoding="utf-8") as mf: 
    print >> mf, "doc-id,review-id,reviewer-id,rating,restaurant,category,row-word-count"   
    for i, tokens in enumerate(doc_tokens):
        doc_t = [token for token in tokens if token in vocab]
        print >> pf, u' '.join(doc_t)
        print >> mf, "%d,%s,%s,%s,%s,%s,%d" % (doc_ids[i], review_ids[i], 
                                               reviewer_ids[i], ratings[i],
                                               restaurants[i], categories[i],
                                               len(doc_t))
        
print "DONE."
