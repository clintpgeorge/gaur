#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
This files contains necessary functions to download the Wikipedia articles 
given a set of specified Wikipedia categories. It uses MediaWiki API to list 
all the articles in a Wikipedia category and grab the article. 

Created on Feb 26, 2014

@author: Clint P. George 
'''

from bs4 import BeautifulSoup
from datetime import datetime
import requests 
import os 
import codecs
import json
import re

MIN_NUM_WORDS = 50 # We ignore pages with less than 50 words 
SECTION_EXCLUSIONS = ['see also', 
                      'references', 
                      'further reading', 
                      'external links', 
                      'bibliography']
NAME_SPACES = [0, 14] # http://www.mediawiki.org/wiki/Manual:Namespace

def query(request):
    '''
    https://www.mediawiki.org/wiki/API:Query
    '''    
    request['action'] = 'query'
    request['format'] = 'json'
    
    lastContinue = dict()
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the 
        # last result.
        req.update(lastContinue)
        # Call API
        result = requests.get('http://en.wikipedia.org/w/api.php', 
                              params=req).json()
        if 'error' in result: 
            print(result['error'])
            break
        if 'info' in result and 'code' in result:
            if 'code' in ['cminvalidcategory', 
                          'cminvalidtitle', 
                          'cmnotitle']:
                print result['info']
                break
        if 'warnings' in result: 
            print(result['warnings'])
        if 'query' in result: 
            yield result['query']
        if 'continue' not in result: 
            break
        lastContinue = result['continue']
        

def get_wikipage_intro(wiki_title, out_format="plaintext"):
    
    intro_text = u""
    if out_format == "plaintext":
        request = {'titles':wiki_title, 
                   'exintro':1, 'explaintext':1, 
                   'exsectionformat':'plain', 
                   'prop':'extracts', 'redirects':1}
    else:
        request = {'titles':wiki_title, 
                   'exintro':1, 
                   'exsectionformat':'plain', 
                   'prop':'extracts', 'redirects':1}
    
    for result in query( request ):
        for _, value in result[u'pages'].items():
            intro_text += value[u'extract']
    
    return intro_text

'''
def get_wikipage_subsections(wiki_title):
    
    wikipage_text = u""
    
    for result in query( {'titles':wiki_title, 
                          'prop':'extracts', 
                          'redirects':1}):
        
        for pageid, value in result[u'pages'].items():
    
            soup = BeautifulSoup(value[u'extract']) # process result data
            sub_header_tags = [sec for sec in soup.findAll('h2') 
                           if sec.get_text(separator = u" ", strip = True).lower() not in SECTION_EXCLUSIONS] # it's a bug 

            for sub_header_tag in sub_header_tags:
                
                wikipage_text += u"\n" + sub_header_tag.get_text(separator=u" ", strip=True) + u"\n"
                nextNode = sub_header_tag
     
                while nextNode:
                    nextNode = nextNode.nextSibling
                    
                    try: tag_name = nextNode.name
                    except AttributeError: tag_name = ""
                    
                    if tag_name == "h2":
                        break
                    elif tag_name:
                        wikipage_text += u" ".join(t.strip() for t in nextNode.findAll(text=True)) + u"\n"
    
    return wikipage_text

'''

def bs_preprocess(html): 
    '''
    remove distracting whitespaces and newline characters
    ''' 
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE) 
    html = re.sub(pat, '', html)        # remove leading and trailing whitespaces 
    html = re.sub('\n', ' ', html)      # convert newlines to spaces 
                                        # this preserves newline delimiters 
    html = re.sub('[\s]+<', '<', html)  # remove whitespaces before opening tags 
    html = re.sub('>[\s]+', '>', html)  # remove whitespaces after closing tags 
    return html 

def get_wikipage(wiki_title):
    
    wikipage_text = u""
    req_dict = {"titles": wiki_title, "prop": "extracts", "redirects": 1}
    
    for result in query(req_dict):
        
        for _, value in result[u"pages"].items(): # pageid
            
            # Removes white spaces and new line characters 
            html_text = bs_preprocess(value[u"extract"])
    
            soup = BeautifulSoup(html_text) # process result data
            
            # Removes empty <p> HTML tags 
            empty_tags = soup.findAll(lambda tag: tag.name == "p" 
                                      and not tag.contents 
                                      and (tag.string is None or 
                                           not tag.string.strip())) 
            [empty_tag.extract() for empty_tag in empty_tags]
            

            sub_header_tags = soup.findAll("h2") 
                           
            
            wikipage_html = "<div id='pagetext'>\n"
            
            if len(sub_header_tags) > 0:
                
                # To retrieve text from the introduction 
                sec_count = 0
                wikipage_html += "<div id='%d'>\n" % sec_count
                for p in reversed(sub_header_tags[0].find_all_previous("p")):
                    wikipage_text += p.get_text(separator = u" ", strip = True) + u" "
                    wikipage_html += p.prettify()
                wikipage_html += "</div>\n"
                wikipage_text += "\n"      
                
                
                # To retrieve text from subsections 
                sec_count += 1
                for sub_header_tag in sub_header_tags:
                    
                    sub_header = sub_header_tag.get_text(separator = u" ", strip = True)
                    if sub_header.lower() in SECTION_EXCLUSIONS: continue
                    
                    wikipage_html += "<div id='%d'>\n" % sec_count
                    wikipage_html += sub_header_tag.prettify()
                    wikipage_text += sub_header + u"\n"
                    
                    nextNode = sub_header_tag   
                    while nextNode:
                        nextNode = nextNode.nextSibling
                        try:
                            tag_name = nextNode.name
                        except AttributeError:
                            tag_name = ""
                        if tag_name == "h2":
                            break
                        elif tag_name:
                            wikipage_text += u" ".join(t.strip() for t in nextNode.findAll(text = True)) + u"\n"
                            wikipage_html += nextNode.prettify()
                    
                    wikipage_html += "</div>\n" 
                    sec_count += 1
            else: 
                wikipage_text += soup.get_text(separator=u" ", strip=True) + u"\n"
                wikipage_html += soup.prettify()
            
            wikipage_html += "</div>\n" 
            
    return wikipage_text, wikipage_html




def get_page_urls(categories, processed_categories):
    '''
    
    >> all_pages = get_page_urls([{'title':'Category:Whales', 'category':''}], [])
    >> for page in all_pages: print page 
    '''
    
    all_pages = []
    sub_categories = []
    
    for category in categories: 
        print 'Querying', category, 
        for result in query({'list':'categorymembers', 
                              'cmprop':'title|type|ids',
                              'cmlimit':500, 
                              'cmtitle':category['title']}):
            
            print len(result['categorymembers']), 'members found.'
            
            for categorymember in result['categorymembers']:
                
                if categorymember['ns'] not in NAME_SPACES: continue                     
                
                if categorymember['type'] == 'subcat':
                    categorytitle = categorymember['title'].strip()
                    if len(categorytitle) == 0: continue 
                    sub_category = {'title':categorytitle, 
                                    'category': ','.join(w for w in [category['category'], category['title']] 
                                                    if len(w.strip()) > 0)}
                    if categorytitle not in [ct['title'] for ct in processed_categories]:
                        sub_categories.append(sub_category)
                
                elif categorymember['type'] == 'page': 
                    categorymember['category'] = category['title'] 
                    categorymember['supercategories'] = category['category'] 
                    all_pages.append(categorymember)
    
    processed_categories += categories
    if len(sub_categories):
        print 'Querying', len(sub_categories), 'subcategories'
        all_pages += get_page_urls(sub_categories, processed_categories)
    
    return all_pages


def slugify(value):
    """
    Normalizes string, removes non-alpha characters,
    and converts spaces to underscores.
    
    Added from: 
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    import unicodedata
    #import re 
    
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip()) 
    
    return unicode(re.sub('[-\s]+', '_', value))

def download_wikipages(page_info_file, pages_dir, all_pages):
    
    if not os.path.exists(pages_dir):
        os.makedirs(pages_dir)

    saved_pages = []
#     allcategories = set([page['category'] for page in all_pages]) 
    count = 0

    for page in all_pages:        
        
        pagetitle = page['title'].strip()

        try: 
            print 'Querying', page, '....',
            introtext = get_wikipage_intro(pagetitle) 
#             sectext = get_wikipage_subsections(pagetitle) 
#             
#             total_text = introtext + u" " + sectext  
            wikipage_text, wikipage_html = get_wikipage(pagetitle)
            
            num_w = len(wikipage_text.split())   
            print "word count:", num_w,            
            
            if num_w < MIN_NUM_WORDS: 
                print "DISCARDED."
                continue
            
#             page_categories = get_page_categories(pagetitle, str(page['pageid']))
#             page_categories = [c for c in page_categories if c in allcategories]
#             page['pagecategories'] = page_categories
        except:
            wikipage_text = ""
            print 'Exceptions.'
            
        if len(wikipage_text) == 0: continue 
         
        try: 
            # This is fix for invalid titles 
            pagepath = os.path.join(pages_dir, pagetitle)
            if os.access(pagepath, os.W_OK):
                page['filename'] = pagetitle
            else:
                page['filename'] = slugify(pagetitle)
                pagepath = os.path.join(pages_dir, page['filename'])

            with codecs.open(pagepath, 'w', encoding='utf-8') as fp:
                print >>fp, wikipage_text
            with codecs.open(pagepath + ".html", 'w', encoding='utf-8') as fp:
                print >>fp, wikipage_html
            with codecs.open(pagepath + ".intro.txt", 'w', encoding='utf-8') as fp:
                print >>fp, introtext
            print "DOWNLOADED."
            
            count += 1
            saved_pages.append(page) 
        except:
            print "Error in saving file."
            
    
    d = {'pages':saved_pages}
    with codecs.open(page_info_file+'.json', 'w', encoding='utf-8') as fw:
        fw.write(unicode(json.dumps(d, ensure_ascii=False)))
    print 'Page index is stored in', page_info_file

    return count 


def get_page_categories(title, pageid):
    
    categories = []
    
    for result in query({'prop':'categories',
                         'titles':title}):
        for cat in result["pages"][pageid][u'categories']:
            categories.append(cat[u'title'])

    return categories
    

def download_and_save(categories, dataset_name, data_dir):
    
    pages_dir = os.path.join(data_dir, 'pages')
    page_info_file = os.path.join(data_dir, dataset_name) 
     
    start_time = datetime.now()
     
    cats = []
    for title in categories:
        cats.append({'title':title, 'category':''})
    all_pages = get_page_urls(cats, [])
     
    count = download_wikipages(page_info_file, pages_dir, all_pages)
         
    print 
    print count, 'articles are downloaded.'
    print 'Execution time:', (datetime.now() - start_time)

    

#===============================================================================
# TEST SCRIPTS 
#===============================================================================


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

# 
# categories = ["Category:Eagles", "Category:Falcons", 
#               "Category:Harriers (birds)", "Category:Hawks", 
#               "Category:Kites (birds)", "Category:Owls", 
#               "Category:Ducks", "Category:Swans", "Category:Ratites"]
# dataset_name = "Birds"
#     
# data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 
# download_and_save(categories, dataset_name, data_dir)


categories = ["Category:Animals"]
dataset_name = "Animals"
data_dir = "E:\\Datasets\\%s" % dataset_name # the download directory 

download_and_save(categories, dataset_name, data_dir)
