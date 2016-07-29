'''

Versions:
    July 11, 2016 - Original version 
References: 
    http://miguelmalvarez.com/2015/03/20/classifying-reuters-21578-collection-with-python-representing-the-data/
    http://www.nltk.org/howto/corpus.html

@author: Clint P. George 
'''
import codecs 
import re
import csv 
from os.path import join
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


 
data_dir = "D:\\data\\lda-hp-data\\birds2"
page_dir_name = "pages"
ds_name = "birds"
min_token_freq = 5
max_token_len = 100
delimiter = ","
file_extension = ""

review_dir = join(data_dir, page_dir_name)  
page_info_file = join(data_dir, ds_name + '.csv') 
categories_file_path = join(data_dir, "%s-cat.csv" % ds_name) 

# Custom stopwords 
stop_words += [u"ax", u"don", u"ll", u"ve", u"didn", u"etc"]

token_stats_file = join(data_dir, "%s.token-stats" % ds_name)
dict_file = join(data_dir, "%s.dict" % ds_name)
ldac_file = join(data_dir, "%s.ldac" % ds_name)
tokens_file = join(data_dir, "%s.tokens" % ds_name)
md_file = join(data_dir, "%s-final.csv" % ds_name)

token_stats = defaultdict(int)
doc_ids = []
doc_raw_wc = []
doc_tokens = []
titles = []
categories = []
num_articles = 0 




# Reads the docs to be processed 
with codecs.open(page_info_file, encoding='utf-8') as fp:
    reader = csv.DictReader(fp, delimiter=delimiter)
    doc_details = []
    for row in reader: 
        row['docpath'] = join(data_dir, page_dir_name, row['title'] + file_extension)
        doc_details.append(row)
    
assert len(doc_details) > 0
print "Number of articles:", len(doc_details)

 
categories_dict = defaultdict(int)
ratings_dict = defaultdict(int)
 
for row in doc_details:
    file_path = row['docpath']
    with codecs.open(file_path, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
        article_text = " ".join(lines)
        tokens = custom_tokenizer(article_text, max_token_len)
        tokens = tokens[:400]
        for token in tokens: 
            token_stats[token] += 1
        raw_word_count = len(article_text.split())
        num_articles += 1
        doc_ids.append(num_articles)
        doc_raw_wc.append(raw_word_count)
        doc_tokens.append(tokens)
        categories.append(row['category'])
        titles.append(row['title'])
 
 
             
      
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
    print >> mf, "doc-id,category,title,row-word-count"   
    for i, tokens in enumerate(doc_tokens):
        doc_t = [token for token in tokens if token in vocab]
        print >> pf, u' '.join(doc_t)
        print >> mf, "%d,%s,%s,%d" % (doc_ids[i], categories[i], titles[i], len(doc_t))

print "DONE."
