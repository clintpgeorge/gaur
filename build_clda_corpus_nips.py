'''
Created on Apr 18, 2016

References: 
    http://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    http://www.nltk.org/howto/corpus.html

@author: clintpg
'''
import codecs 
import os
import re
from os.path import join
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


 
data_dir = "D:\\data\\clda-data\\nips-00-18"
data_folders = ["nips13", "nips14", "nips15", "nips16", "nips17", "nips18"]
ds_name = "nips-13-18"
min_token_freq = 20
min_token_len = 2
max_token_len = 100
min_doc_length = 20
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
doc_fn = []
doc_raw_wc = []
doc_tokens = []
doc_coll = []
num_articles = 0 

with codecs.open(metadata_file_path, "w", encoding="utf-8") as mf: 
    # metadata header 
    print >> mf, "doc-id,file-name,raw-word-count,collection"        
        
    for df_name in data_folders:
        df_path = join(data_dir, df_name)
        for file_name in os.listdir(df_path):
            if not file_name.endswith(".txt"): 
                continue
    
            print "processing", file_name
            
            article_text = ""
            file_path = join(df_path, file_name)
            with codecs.open(file_path, "r", encoding="utf-8", errors='ignore') as f: 
                article_text = f.read()
                
            tokens = custom_tokenizer(article_text, min_token_len, max_token_len)
            for token in tokens: 
                token_stats[token] += 1
            
            
            raw_word_count = len(article_text.split())
            num_articles += 1
            print >> mf, "%d,%s,%d,%s" % (num_articles, file_name, 
                                          raw_word_count, df_name)
            
            doc_ids.append(num_articles)
            doc_raw_wc.append(raw_word_count)
            doc_tokens.append(tokens)
            doc_coll.append(df_name)
            doc_fn.append(file_name)
            
     
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
    print >> mf, "doc-id,file-name,raw-word-count,word-count,collection"         
    for i, tokens in enumerate(doc_tokens):
        doc_t = [token for token in tokens if token in vocab]
        print >> pf, u' '.join(doc_t)
        print >> mf, "%d,%s,%d,%d,%s" % (doc_ids[i], doc_fn[i], doc_raw_wc[i],
                                         len(doc_t), doc_coll[i])
        
print "DONE."
