Gaur 
====

It's a project to create topic modeling / text classification data sets using 
the Wikipedia articles. The user has to specify the Wikipedia categories of 
interest to download the associated articles and create a data set out of it. 
This project uses the [MediaWiki API] to query all articles in a Wikipedia 
category and download articles' textual content. 

Usage
-----
* To download the Wikipedia articles, see ***download_wikipedia_articles.py***
* To build a topic modeling data set (in the [LDA-C] format), see ***build_ldac_corpus.py*** 


Dependencies
------------

* The [Gensim] package (to create a topic modeling dataset in the [LDA-C] format) 
* The [MediaWiki API]
   
[MediaWiki API]:http://www.mediawiki.org/wiki/API:Main_page
[Gensim]:http://radimrehurek.com/gensim/
[LDA-C]:http://www.cs.princeton.edu/~blei/lda-c/readme.txt
