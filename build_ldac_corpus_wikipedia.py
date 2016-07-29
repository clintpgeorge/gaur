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

# import os 
import re 
import codecs
import logging
import json 
import csv 
import locale
from gensim import corpora
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from dateutil import parser
from fractions import Fraction
from os.path import exists, join, splitext
from collections import defaultdict

locale.setlocale(locale.LC_NUMERIC, 'US')
    
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

'''
Global variables 
'''
category_filter = []
STRIP_CHAR_LIST = [u'_', u'-', u',', u'!', u':', u'.', u'?', 
                   u';', u'=', u'�', u'�', u'�', u'�', u'�', 
                   u'�', u'�', u'�', u'�', u'*', u'~', u'`', 
                   u':', u'<', u'>', u'{', u'}',
                   u'[', u']', u'//', u'(', u')'] 
REMOVE_LIST = [u"[", u"]", u"{", u"}", u"(", u")", u"'", u".", 
               u"..", u"...", u",", u"?", u"!", u"/", u"\"", 
               u"\"", u";", u":", u"-", u"`", u"~", u"@", u"$", 
               u"^", u"|", u"#", u"=", u"*"];

numeric_parser = re.compile(r"""        # A numeric string consists of:
    (?P<sign>[-+])?              # an optional sign, followed by either...
    (    
        (?=\d|\.\d)              # ...a number (with at least one digit)
        (?P<int>\d*)             # having a (possibly empty) integer part
        (\.(?P<frac>\d*))?       # followed by an optional fractional part
        (E(?P<exp>[-+]?\d+))?    # followed by an optional exponent, or...
    |
        Inf(inity)?              # ...an infinity, or...
    |
        (?P<signal>s)?           # ...an (optionally signaling)
        NaN                      # NaN
        (?P<diag>\d*)            # with (possibly empty) diagnostic info.
    )
    \Z
""", re.VERBOSE | re.IGNORECASE | re.UNICODE).match
    
date_parser = re.compile(r'''(\d{2})[/.-](\d{2})[/.-](\d{4})$''',
                         re.VERBOSE | re.IGNORECASE | re.UNICODE).match
time_parser = re.compile(r'''(\d{2}):(\d{2}):(\d{2})$''',
                         re.VERBOSE | re.IGNORECASE | re.UNICODE).match
time_parser2 = re.compile(r'''(\d{2}):(\d{2})$''',
                         re.VERBOSE | re.IGNORECASE | re.UNICODE).match
'''
Initializes the tokenizer, lemmatizer, and stemmer  
'''
# Manages real numbers, numbers with comma separators, 
# dates, times, hyphenated words, email addresses, urls 
# and abbreviations
# https://code.google.com/p/nltk/issues/detail?id=128
pat1 = r'''(?:[A-Z][.])+|\d[\d,.:\-/\d]*\d|\w+[\w\-\'.&|@:/]*\w+'''

pat2 = r'''\w+|\$[\d\.]+|\S+'''

# https://code.google.com/p/nltk/issues/detail?id=128
pat3 = r'''(?x)    # set flag to allow verbose regexps
        ([A-Z]\.)+        # abbreviations, e.g. U.S.A. 
        | \w+(-\w+)*        # words with optional internal hyphens
        | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
        | \.\.\.            # ellipsis
        | [][.,;"'?():-_`]  # these are separate tokens
        '''

regx_tokenizer = RegexpTokenizer(pat1)

# punkt_tokenizer = PunktWordTokenizer()
wordnet_lmtzr = WordNetLemmatizer()
porter_stemmer = PorterStemmer() 

def xstr(s):
    return '' if s is None else str(s)

def is_date(token):
    try:
        parser.parse(token)
    except:
        return False
    return True 

def is_numeric(num_str):
    try:
        float(num_str)
        return True 
    except ValueError:
        try:
            locale.atof(num_str)
            return True 
        except ValueError:
            try:
                float(Fraction(num_str))
                return True 
            except ValueError:
                return False  


def load_en_stopwords(filename):
    '''Loads English stop-words from a given file 
    
    Return: 
        a list of stop words
    Arguments: 
        the stop-words file name
    '''
    
    stopwords = []
    with codecs.open(filename, mode='r', encoding='utf-8') as fSW: 
        for line in fSW: 
            stopwords.append(line.strip().lower())
    return stopwords

stop_words = stopwords.words('english')

def remove_non_ASCII(s): 
    return u"".join(i for i in s if ord(i) < 128)
    
def cleanup(token):
    '''Clean up a given token based on regular expression, strip(),
    and a predefined set of characters 
    
    Returns: 
        a cleaned up token 
    Arguments:
        a token (str) 
    '''
    try:
        
        token = remove_non_ASCII(token)

        # It's commented because it will remove slashes in a URL 
        # token = re.sub('[\(\)\{\}\[\]\'\"\\\/*<>|]', '', token) 

        for each_char in STRIP_CHAR_LIST:
            token = token.strip(each_char)
            if token.endswith(u"'s"): token = token.rstrip(u"'s")            
        
        if ((token in REMOVE_LIST) # removes if it's in the remove list 
            or (token in stop_words) # removes stop words  
            or is_date(token) # discards if it's a date  
            or is_numeric(token)): # discards if it's a numeric
            return ''

    except: 
        return '' 
    
    return token.strip()



def regex_tokenizer(text):
    '''A tokenizer based on NLTK's RegexpTokenizer 
    
    Returns: 
        a list of tokens 
    Arguments:
        a string to tokenized 
    
    '''

    tokens = regx_tokenizer.tokenize(text)

    filtered = []
    for w in tokens:
        try:
            token = cleanup(w.lower()) 
            if len(token) > 0: 
                filtered.append(token)
        except: 
            pass 

    return filtered

   
   
# def punkt_word_tokenizer(text):
#     '''A tokenizer based on NLTK's PunktWordTokenizer 
#     
#     Returns: 
#         a list of tokens 
#     Arguments:
#         a string to tokenized 
#     
#     '''
#     try: 
#         text = ' '.join(text.lower().split()) # removes newline, tab, and white space
#     except Exception:
#         pass  
#           
#     tokens = punkt_tokenizer.tokenize(text)
#     
#     print tokens 
#     # tokens = [cleanup(w) for w in tokens]
#     # tokens = [w for w in tokens if w not in REMOVE_LIST]
#     filtered = []
#     for w in tokens:
#         try: 
#             w = cleanup(w)
#             if len(w) > 0: 
#                 for wt in w.split(','): 
#                     filtered.append(wt)
#         except: 
#             pass 
#     
#     return filtered

def whitespace_tokenize(doc_text):
    '''
    This function will tokenize the given 
    document text into tokens  based on whitespace 
    
    '''
    return doc_text.lower().split()



def lemmatize_tokens(word_tokens):
    '''
    Lemmatize tokens based on WordNet 
    '''
    tokens = [] 
    for token in word_tokens:
        try:
            # print 'lemma:', token, '-->', wordnet_lmtzr.lemmatize(token)   
            token = wordnet_lmtzr.lemmatize(token)
        except: pass 
        tokens.append(token)
    
    return tokens


def stem_tokens(word_tokens):
    '''
    Stem tokens based on Snowball stemmer  
    '''
    tokens = [] 
    for token in word_tokens:
        try:
            # print 'stem:', token, '-->', porter_stemmer.stem(token)   
            token = porter_stemmer.stem(token)
        except: pass 
        tokens.append(token)
        
    return tokens


def _process_doc(doc):
    '''Processes a single indexed document  
    
    Arguments: 
        doc - a document's details in the index file 
    '''
    
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            with codecs.open(doc[u'docpath'], 'r', body_charset) as fp:
                doc_text = fp.read()
                doc_text = doc_text.encode('UTF-8') # encodes to UNICODE 
        except UnicodeError: pass
        else: break
    
    tokens = regex_tokenizer(doc_text)
    tokens = lemmatize_tokens(tokens)
    # tokens = stem_tokens(tokens)
    
    tokens = [w for w in tokens if w not in stop_words] # double checking 
        
    return tokens


def create_dictionary(doc_details, dictionary_file, min_word_freq, 
                      min_word_len, max_word_len):
    '''
    Creates a dictionary from the given text files 
    using the Gensim class and functions
    
    Returns:
        None 
    Arguments:
        doc_details - a list of documents to be processed  
        dictionary_file - the dictionary object file (output)
        min_word_freq - min frequency of a valid vocabulary term 
        min_word_len - min word length of a valid vocabulary term 
        max_word_len - max word length of a valid vocabulary term
    '''

    # collect statistics about all tokens
    # doc_id, category, subject, doc_path
    dictionary = corpora.Dictionary(_process_doc(doc) for doc in doc_details) 
    
    # remove words that appear < MIN_FREQUENCY 
    # remove words that have word length < MIN_WORD_LENGTH
    # remove words that have word length > MAX_WORD_LENGTH    
    filter_ids = [] 
    filter_ids += [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() 
                   if docfreq < min_word_freq]
    filter_ids += [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() 
                   if (len(dictionary[tokenid]) < min_word_len)]
    filter_ids += [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() 
                   if (len(dictionary[tokenid]) > max_word_len)]
    
    dictionary.filter_tokens(filter_ids) # remove filtered words 
    dictionary.compactify() # remove gaps in id sequence after words that were removed
    dictionary.save(dictionary_file) # store the dictionary, for future reference
    
    logging.info(str(dictionary))



class TextCorpus(object):
    '''The text corpus class 
    '''
    
    def __init__(self, dictionary, doc_details):
        '''
        Constructor 
        
        Returns: 
            a corpus object 
        Arguments: 
            dictionary - a dictionary object 
            doc_details - the document's path index file
        '''
        
        self._doc_details = doc_details               
        self._dictionary = dictionary
         
    def __iter__(self):

        for doc in self._doc_details:
            tokens = _process_doc(doc)
            yield self._dictionary.doc2bow(tokens)


def _create_ldac_corpus(doc_details, 
                        dictionary_file, 
                        ldac_file, 
                        min_word_freq, 
                        min_word_len, 
                        max_word_len, 
                        delimiter):
    
    # Creates the dictionary and the Blei corpus 
    create_dictionary(doc_details, dictionary_file, min_word_freq, min_word_len, 
                          max_word_len)
    dictionary = corpora.Dictionary().load(dictionary_file)    
    corpus = TextCorpus(dictionary, doc_details) 
    corpora.BleiCorpus.serialize(ldac_file, corpus, id2word=dictionary)
    logging.info('The Blei corpus is created.')
    
    
    # Saves index to a CSV file 
    
    index_file = splitext(ldac_file)[0] + '.csv'
    fdnames = [u'collection', u'category', u'title', u'pageid', 
               u'uniquewordcount', u'doclength', u'category-path', u'docpath'] 

    
    with codecs.open(index_file, 'wb', encoding = 'utf-8') as fw:
        dw = csv.DictWriter(fw, 
                            delimiter = delimiter, 
                            fieldnames = fdnames, 
                            extrasaction = 'ignore')
        dw.writeheader()
        for doc_id, doc in enumerate(corpus): 
            rowdict = doc_details[doc_id]
            rowdict[u'title'] = rowdict[u'filename']
            rowdict[u'uniquewordcount'] = len(doc)
            rowdict[u'doclength'] = sum(count for _, count in doc)
            dw.writerow(rowdict)



def build_ldac_corpus_json(page_info_file, 
                           pages_dir, 
                           dict_file, 
                           ldac_file, 
                           min_word_freq = 5, 
                           min_word_len = 2, 
                           max_word_len = 20, 
                           delimiter = ';', 
                           file_extension = '', 
                           even_pages = False):
    '''
    This function reads a JSON index file created by download_wikipedia_*.py 
    and creates a LDA-C formatted corpus and dictionary using the Gensim package 
    
    Rivisions: 
        Feb 16, 2016 - rechecked the function flow 
    
    '''

    
    
    doc_details = []
    cat_size = defaultdict(int)
    cat_cnt = defaultdict(int)
    
    # Reads the document details from JSON index file 
    with codecs.open(page_info_file, encoding='utf-8') as fp:
        json_data = json.load(fp)
        sorted_pages = sorted(json_data[u'pages'], key=lambda k: k[u'category']) 
        
        for page in sorted_pages:            
            if (page[u'category'] in category_filter) or (not category_filter): 
                cat_size[page[u'category']] += 1
        logging.info("Category page counts: %s", str(cat_size))
        avg_page_count = sum(cat_size.values()) / len(cat_size)
        logging.info("Max count: %d", avg_page_count)
        
        for page in sorted_pages:            
            if (page[u'category'] in category_filter) or (not category_filter): 
                
                if (even_pages 
                    and page[u'category'] in cat_cnt 
                    and cat_cnt[page[u'category']] > avg_page_count): 
                    continue
                cat_cnt[page[u'category']] += 1
                
                if exists(join(pages_dir, page[u'title'] + file_extension)):
                    page[u'docpath'] = join(pages_dir, page[u'title'] + file_extension)
                    doc_details.append(page)
                elif u'filename' in page:
                    if exists(join(pages_dir, page[u'filename'] + file_extension)):
                        page[u'docpath'] = join(pages_dir, page[u'filename'] + file_extension)
                        doc_details.append(page)
                        
    assert len(doc_details) > 0

    _create_ldac_corpus(doc_details, dict_file, ldac_file, min_word_freq, 
                        min_word_len, max_word_len, delimiter)

    


def build_ldac_corpus_csv(page_info_file, dict_file, ldac_file, 
                          min_word_freq=5, min_word_len=2, max_word_len=20, 
                          delimiter=','):
    '''
    This function reads the page index file (CSV file) and creates an LDA-C 
    formatted corpus and vocabulary
    
    CSV header: 
    ----------
    pageid,category,title,uniquewordcount,doclength,supercategories,docpath
    
    Last modified on: August 05, 2015 
     
    '''

    # Reads the docs to be processed 
    with codecs.open(page_info_file, encoding='utf-8') as fp:
        reader = csv.DictReader(fp, delimiter=delimiter)
        doc_details = [row for row in reader]
    assert len(doc_details) > 0
    print "Number of articles:", len(doc_details)

    _create_ldac_corpus(doc_details, dict_file, ldac_file, min_word_freq,
                        min_word_len, max_word_len, delimiter)




def build_ldac_corpus2_csv(doc_path_index_file, data_folder, dictionary_file, 
                          ldac_file, min_word_freq=5, min_word_len=2, 
                          max_word_len=20, delimiter=';'):
    '''
    This function reads documents' details from a CSV formatted file and build 
    the LDA-C formatted corpus and vocabulary. 
    
    The CSV headers are a little different from new data sets. This is kept 
    unchanged to handle backward compatibility. This function is mainly for 
    datasets such as whales-tires, whales-tires-mixed, whales-tires-reduced 
    and their variants. These datasets are not created using the python 
    script download_wikipedia_articles.py   
    
    CSV Header Format:
    doc-id;category;sub-category;title;unique-word-count;doc-length
    '''
    
    # Reads the docs to be processed 
    doc_details = []
    with open(doc_path_index_file) as fp: 
        reader = csv.DictReader(fp, delimiter=delimiter)
        for row in reader:
            row['docpath'] = join(data_folder, row[u'title'])
            doc_details.append(row)
    assert len(doc_details) > 0

    # Creates the dictionary 
    create_dictionary(doc_details, dictionary_file, 
                      min_word_freq, min_word_len, max_word_len)
     
    # Creates the corpus 
    dictionary = corpora.Dictionary().load(dictionary_file)       
    corpus = TextCorpus(dictionary, doc_details) # doesn't load the corpus into the memory!
    corpora.BleiCorpus.serialize(ldac_file, corpus, id2word=dictionary)
     
 
    # Saves the file index     
    index_file = splitext(ldac_file)[0] + '.index'
    fdnames = ['doc-id', 'category', 'sub-category', 'title', 
               'unique-word-count', 'doc-length']
    with open(index_file, 'wb') as fw:
        dw = csv.DictWriter(fw, delimiter=delimiter, 
                            fieldnames=fdnames, 
                            extrasaction='ignore')
        dw.writeheader()
        for doc_id, doc in enumerate(corpus): 
            rowdict = doc_details[doc_id]
            rowdict['unique-word-count'] = len(doc)
            rowdict['doc-length'] = sum(count for _, count in doc)
            dw.writerow(rowdict)
  
         
    logging.info('The Blei corpus building is completed.')





def build_ldac_corpus_csv3(page_info_file, pages_dir, dictionary_file, 
                           ldac_file, min_word_freq=2, min_word_len=2, 
                           max_word_len=100, delimiter=',', file_extension=''):
    '''
    This function reads the page info CSV file and creates a LDA-C formatted 
    corpus and vocabulary using the Gensim package 
    
    Format of a single line CSV: 
        collection,category,title,pageid,uniquewordcount,doclength,category-path,docpath
        
    
    '''

    # Reads the docs to be processed 
    with codecs.open(page_info_file, encoding='utf-8') as fp:
        reader = csv.DictReader(fp, delimiter=delimiter)
        doc_details = []
        for row in reader: 
            row['docpath'] = join(pages_dir, row['title'] + file_extension)
            doc_details.append(row)
        
    assert len(doc_details) > 0
    print "Number of articles:", len(doc_details)

    _create_ldac_corpus(doc_details, dictionary_file, ldac_file, min_word_freq,
                        min_word_len, max_word_len, delimiter=';')



stop_words = load_en_stopwords('en_stopwords') 
print 'Number of stop words:', len(stop_words)
