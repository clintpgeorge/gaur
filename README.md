gaur 
====

This project provides **libraries** to create datasets for topic modeling or text classification. This also has a **pure python** implementation of the collapsed Gibbs sampling algorithm of the topic model Latent Dirichlet Allocation (Caveat: It's not written handling large datasets).   

Currently, it supports to download articles from the English wikipedia and create datasets. The user has to specify the Wikipedia categories of interest to download the associated articles and create a data set out of it. This project uses the [MediaWiki API] to query all articles in a Wikipedia category and download articles' text. 

Usage
-----
* To download the Wikipedia articles, see ***download_wikipedia_articles.py***
* To build a topic modeling data set (in the [LDA-C] format), see ***build_ldac_corpus.py*** 
* To run the LDA collapsed Gibbs sampling algorithm, see ***lda_gibbs.py*** and ***lda_gibbs_test*.py***


Dependencies
------------

* The [Gensim] package (to create a topic modeling dataset in the [LDA-C] format) 
* The [MediaWiki API]
   
[MediaWiki API]:http://www.mediawiki.org/wiki/API:Main_page
[Gensim]:http://radimrehurek.com/gensim/
[LDA-C]:http://www.cs.princeton.edu/~blei/lda-c/readme.txt
