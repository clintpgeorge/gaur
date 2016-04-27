'''
Created on Apr 2, 2016

References: 
    http://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    http://www.nltk.org/howto/corpus.html

@author: clintpg
'''
import codecs 
import os
import re
from bs4 import BeautifulSoup
from os.path import join, exists
from collections import defaultdict
from gensim import corpora
from utils_text import stop_words, is_date, is_numeric, STRIP_CHARS

pattern = re.compile('[\W_]+')

def custom_tokenizer(doc_text, min_token_len, max_token_len):
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
                    or len(token) < min_token_len
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


 
data_dir = "D:\\data\\clda-data\\reuters-21578"
ds_name = "reuters-21578"
min_token_freq = 10
min_token_len = 2
max_token_len = 100
min_doc_length = 20 
max_doc_length = 800 

# Custom stopwords 
stop_words += [u"ax", u"don", u"ll", u"ve", u"didn", u"etc"]

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

article_dir = join(data_dir, "articles")  
if not exists(article_dir): os.makedirs(article_dir)
topic_stats_file_path = join(data_dir, "%s.topics" % ds_name)  
place_stats_file_path = join(data_dir, "%s.places" % ds_name)  
loc_stats_file_path = join(data_dir, "%s.locations" % ds_name)  
metadata_file_path = join(data_dir, "%s-raw.csv" % ds_name)  
token_stats_file = join(data_dir, "%s.token-stats" % ds_name)
dict_file = join(data_dir, "%s.dict" % ds_name)
ldac_file = join(data_dir, "%s.ldac" % ds_name)
tokens_file = join(data_dir, "%s.tokens" % ds_name)
md_file = join(data_dir, "%s.csv" % ds_name)


topic_stats = defaultdict(int)
place_stats = defaultdict(int)
token_stats = defaultdict(int)
loc_stats = defaultdict(int)
num_articles = 0
num_articles_w_place = 0
num_articles_w_topic = 0
num_articles_w_loc = 0
doc_ids = []
doc_topics = []
doc_places = []
doc_dates = []
doc_titles = []
doc_raw_wc = []
doc_tokens = []
doc_loc = []
doc_coll = []

with codecs.open(metadata_file_path, "w", encoding="utf-8") as mf: 
    
    for sgm_file_name in os.listdir(data_dir):
        if not sgm_file_name.endswith(".sgm"): continue
    
        print "processing", sgm_file_name
     
        sgm_file_path = join(data_dir, sgm_file_name)
        sf = codecs.open(sgm_file_path, "r", encoding="ISO-8859-1")
        soup = BeautifulSoup(sf.read(), "xml")
        articles = soup.find_all("REUTERS")
         
        # metadata header 
        print >> mf, "new-id,topics,places,date,title,raw-word-count,location,collection"        
        
        for article in articles:
            new_id = article["NEWID"]
            topic_tags = ""
            place_tags = ""
            article_date = ""
            if article.TOPICS:
                topic_tags = article.TOPICS.get_text(separator = u" ", strip = True)
                for tag in topic_tags.split():
                    topic_stats[tag] += 1
                     
            if article.PLACES:
                place_tags = article.PLACES.get_text(separator = u" ", strip = True)
                for tag in place_tags.split():
                    place_stats[tag] += 1
                 
            if article.DATE:
                article_date = article.DATE.get_text(separator = u" ", strip = True)
            article_text = ""
            article_title = ""
            article_location = ""
            if article.TEXT:
                if article.TEXT.TITLE:
                    article_title = article.TEXT.TITLE.get_text(separator = u" ", strip = True)  
                if article.TEXT.DATELINE: 
                    article_dateline = article.TEXT.DATELINE.get_text(separator = u" ", strip = True)  
                    article_location = "|".join(w.strip() for w in article_dateline.split(",")[:-1] if len(w.strip()) > 0)
                    
                if article.TEXT.BODY: 
                    article_text = article.TEXT.BODY.get_text(separator = u" ", strip = True)
                else:
                    article_text = article.TEXT.get_text(separator = u" ", strip = True)
            raw_word_count = len(article_text.split())
            
            num_articles += 1
            if len(topic_tags) > 0: num_articles_w_topic += 1
            
            # Consider only articles with place tags 
            
            if len(place_tags) > 0: 
                num_articles_w_place += 1
                
                if len(article_location) > 0: 
                    num_articles_w_loc += 1
                    loc_stats[article_location] += 1
                
                places = place_tags.split()
                collection = "rest"
                if contains(europe, places):
                    collection = "europe"
                elif contains(asia, places):
                    collection = "asia"
                elif (place_tags == "usa" or place_tags == "canada" or place_tags == "american-samoa"): 
                    collection = "america"
    
                
                with codecs.open(join(article_dir, new_id), "w", encoding="ISO-8859-1") as af:
                    print >> af, article_text
                
                article_title = pattern.sub(' ', article_title)
                print >> mf, "%s,%s,%s,%s,%s,%d,%s,%s" % (new_id, topic_tags, 
                                                       place_tags, article_date, 
                                                       article_title, 
                                                       raw_word_count, 
                                                       article_location, 
                                                       collection)
                
                tokens = custom_tokenizer(article_text, min_token_len, max_token_len)
                for token in tokens: token_stats[token] += 1
                
                doc_ids.append(new_id)
                doc_topics.append(topic_tags)
                doc_places.append(place_tags)
                doc_dates.append(article_date)
                doc_titles.append(article_title)
                doc_raw_wc.append(raw_word_count)
                doc_tokens.append(tokens)
                doc_loc.append(article_location)
                doc_coll.append(collection)
            
            if (num_articles % 100) == 0: print ".", 
    
        print 

print "Total number of articles:", num_articles
print "Total number of articles (w/ topics):", num_articles_w_topic
print "Total number of articles (w/ places):", num_articles_w_place
print "Total number of articles (w/ location):", num_articles_w_loc
     
with codecs.open(topic_stats_file_path, "w", encoding="utf-8") as tsf:
    print >> tsf, "topic,counts"
    for k, v in topic_stats.items():
        print >> tsf, k, v
         
with codecs.open(place_stats_file_path, "w", encoding="utf-8") as psf:
    print >> psf, "place,counts"
    for k, v in place_stats.items():
        print >> psf, k, v
        
with codecs.open(token_stats_file, "w", encoding="utf-8") as tf: 
    print >> tf, "token,counts"
    for (k,v) in token_stats.items():
        print >> tf, "%s,%d" % (k, v)
 
with codecs.open(loc_stats_file_path, "w", encoding="utf-8") as lf: 
    print >> lf, "location,counts"
    for (k,v) in loc_stats.items():
        print >> lf, "%s,%d" % (k, v)

###############################################################################    
# Creates the corpus dictionary
###############################################################################

dictionary = corpora.Dictionary(doc_tokens)        
filter_ids = [tid for tid, docfreq in dictionary.dfs.iteritems() 
              if (docfreq < (min_token_freq / 2))]
dictionary.filter_tokens(filter_ids) 
dictionary.compactify() 
vocab = dictionary.token2id.keys()

print dictionary



################################################################################
## Removes documents with word count < min_doc_length
################################################################################
num_docs = len(doc_tokens)
print "Number of documents:", num_docs
print "Deleting documents with size <", min_doc_length, "and >", max_doc_length
i = 0
del_cnt = 0
while i < num_docs:
    doc_len = sum(1 for token in doc_tokens[i] if token in vocab)
    while ((doc_len < min_doc_length) or (doc_len > max_doc_length)) and (i < num_docs):
        print ".", 
        del doc_ids[i]
        del doc_topics[i]
        del doc_places[i]
        del doc_dates[i]
        del doc_titles[i]
        del doc_raw_wc[i]
        del doc_tokens[i]
        del doc_loc[i]
        del doc_coll[i]

        num_docs -= 1
        del_cnt += 1        
        if i < num_docs:
            doc_len = sum(1 for token in doc_tokens[i] if token in vocab)
    i += 1
print 
print "Number of documents deleted:", del_cnt
print "Number of remaining documents:", len(doc_tokens)

###############################################################################    
# Re-creates the corpus dictionary
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
    print >> mf, "new-id,topics,places,date,title,raw-word-count,word-count,location,collection"         
    for i, tokens in enumerate(doc_tokens):
        doc_t = [token for token in tokens if token in vocab]
        print >> pf, u' '.join(doc_t)
        print >> mf, "%s,%s,%s,%s,%s,%d,%d,%s,%s" % (doc_ids[i], doc_topics[i],
                                                  doc_places[i], doc_dates[i],
                                                  doc_titles[i], doc_raw_wc[i],
                                                  len(doc_t), doc_loc[i],doc_coll[i])
        
print "DONE."

