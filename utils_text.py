# -*- coding: utf-8 -*-
"""Utility functions for processing document texts 

Versions:
    Updated on Mon Mar 02 10:16:45 2015
    Originally created on Jan 29, 2013 (smarter-eval (repo.), utils_email.py)  

@author: Clint
"""

import quopri
import codecs
import locale
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import SnowballStemmer
from dateutil import parser
from fractions import Fraction


locale.setlocale(locale.LC_NUMERIC, 'US')

'''
Global variables 
'''


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
# Updated on June 26, 2014 
pat4 = r'''(?x)                    # set flag to allow verbose regexps
        ([A-Z]\.)+                 # abbreviations, e.g. U.S.A. 
        | \d[\d,.:\-/\d]*\d        # currency and percentages, e.g. $12.40, 82%
        | \w+[\w\-_\.&|@:/]*\w+    # words with optional internal hyphens
        | \.\.\.                   # ellipsis
        | [][.,;"'?():-_`]         # these are separate tokens
        '''


regx_tokenizer = RegexpTokenizer(pat4)

# punkt_tokenizer = PunktWordTokenizer()
wordnet_lmtzr = WordNetLemmatizer()
snowball_stemmer = SnowballStemmer("english") # Choose a language

def xstr(s):
    return '' if s is None else str(s)

def is_date(token):
    try:
        parser.parse(token)
        return True
    except:
        return False
     

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
            except:
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

stop_words = load_en_stopwords('en_stopwords')
# print 'Number of stop words:', len(stop_words)
STRIP_CHARS = u''.join([u'_', u'-', u',', u'!', u':', u'.', u'?', u';', 
                        u'=', u'…', u'•', u'–', u'¿', u'¡', u'º', u'ª', 
                        u'«', u'»', u'*', u'~', u'`', u':', u'<', u'>', 
                        u'{', u'}', u'[', u']', u'/', u'\\', u'(', u')', 
                        u'@', u'^', u'&', u'|', u'"', u'\'', u'#', u'$', 
                        u'%']) 
stop_words += [u"[", u"]", u"{", u"}", u"(", u")", u"'", u".", u"..", 
               u"...", u",", u"?", u"!", u"/", u"\"", u"\"", u";", u":", 
               u"-", u"`", u"~", u"@", u"$", u"^", u"|", u"#", u"=", u"*"]


def cleanup(token):
    '''Clean up a given token based on regular expression, strip(),
    and a predefined set of characters 
    
    Returns: 
        a cleaned up token 
    Arguments:
        a token (str) 
    '''


    # token = quopri.decodestring(token).encode('UTF-8')
    token = token.strip(STRIP_CHARS)
    
    if (token in stop_words # removes if it's in the remove list 
        or is_date(token) # discards if it's a date  
        or is_numeric(token)): # discards if it's a numeric
        return None 
    else:  
        return token

def regex_tokenizer(text):
    '''A tokenizer based on NLTK's RegexpTokenizer 
    
    Returns: 
        a list of tokens 
    Arguments:
        a string to tokenized 
    
    '''
          
    tokens = regx_tokenizer.tokenize(text)
    cleaned_tokens = []
    for w in tokens:
        try: 
            token = cleanup(w.lower()) 
            if token and len(token) > 0: 
                cleaned_tokens.append(token)
        except: 
            pass  
    return cleaned_tokens

   
#    
# def punkt_word_tokenizer(text):
#     '''A tokenizer based on NLTK's PunktWordTokenizer 
#     
#     Returns: 
#         a list of tokens 
#     Arguments:
#         a string to tokenized 
#     
#     '''
#     try: text = ' '.join(text.lower().split()) 
#     except Exception: pass  
#     tokens = punkt_tokenizer.tokenize(text)
#     
#     cleaned_tokens = []
#     for w in tokens:
#         try: token = cleanup(w.lower()) 
#         except: pass 
#         if len(token) > 0: 
#             for wt in token.split(','): 
#                 cleaned_tokens.append(wt)
# 
#     return cleaned_tokens


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
        try: token = wordnet_lmtzr.lemmatize(token)
        except: pass 
        tokens.append(token)
    return tokens


def stem_tokens(word_tokens):
    '''
    Stem tokens based on Snowball stemmer  
    '''
    tokens = [] 
    for token in word_tokens:
        try: token = snowball_stemmer.stem(token)
        except: pass 
        tokens.append(token)        
    return tokens
