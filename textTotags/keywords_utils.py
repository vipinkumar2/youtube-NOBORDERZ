# -*- coding: utf-8 -*-
# from selenium import webdriver
import time
import json
import nltk
import requests
import unicodecsv as unicodecsv
from bs4 import BeautifulSoup
import urllib
import spacy

# driver=webdriver.Chrome()
def write_output(output, all_data):
    with open(output_file, mode="a") as csvFile:
        row = unicodecsv.writer(csvFile, delimiter=",", lineterminator="\n")
        row.writerow(all_data)


def get_links(keyword):
    n = 0
    word = keyword
    all_tags = []

    while n < 1:
        pge_url = (
            "https://top-hashtags.com/search/?q="
            + word
            + "&opt=top&sp="
            + str(n + 1)
            + ""
        )
        page = requests.get(pge_url)
        soup = BeautifulSoup(page.text, "lxml")

        links = soup.find_all("ul", class_="i-group")[0].find_all("li", class_="i-row")
        for l in links:
            li = l.find_all("div", class_="i-tag")[0].text
            all_tags.append(li)
            # print (all_tags)

            # all_data=[li]
            # write_output(output_file,all_data)
        n = n + 1
    return all_tags


# In[31]:


def text_to_tags(text):
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    stop_words = set(stopwords.words("english"))

    word_tokens = word_tokenize(text)
    tags = []

    for w in word_tokens:
        if w not in stop_words:
            if len(w) > 3:
                tags.append(w)
    return tags


# In[51]:


def check_similarity(textA, textB):
    nlp = spacy.load("en_vectors_web_lg")
    token = textA + " " + textB
    token = nlp(token)
    tokenA = token[0]
    print(token)
    for i in token:
        print(tokenA.similarity(i))


# In[63]:


# this main function generte tags from keyword ot text
def tagss(text):
    tags = []
    tag = text_to_tags(text)
    for i in tag:
        tag = get_links(i)
        tag = " ".join(tag)
        tags.append(tag)

    tag = " ".join(tags)
    return tag


# In[64]:


# tag = tagss('I forgot to give you an off-shot\nI enjoyed shooting with walnuts ☺️💖\nI like this walnut! Face 😳')
# print(tagss('beautifull'))
# Scrapes top trending tags according to keyword (30 tags)
# In[65]:


# In[ ]:
