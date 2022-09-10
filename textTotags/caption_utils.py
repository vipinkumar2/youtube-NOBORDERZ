import os

import torch
import torchtext

# The first time you run this will download a ~823MB file

# All hashtags base on globaly
# in this function load all hashtags from the csv file


def load_glove(glove):
    if glove == None:
        glove = torchtext.vocab.GloVe(
            name="6B", dim=50  # trained on Wikipedia 2014 corpus
        )
        # print('true')
        # embedding size = 100


def hashtags_file():
    import pandas as pd

    # os.chdir(os.getcwd())
    df = pd.read_csv(
        "/home/pc/workspace/new_surviral/surviral_web/textTotags/Monday_hashtags.csv"
    )
    hashtag = df["#recent4recent"].tolist()
    return hashtag


# keyword geting from text after clearing the text


def text_to_tags(text):
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    stop_words = set(stopwords.words("english"))

    word_tokens = word_tokenize(text)
    tags = []

    for w in word_tokens:
        if w not in stop_words:
            if len(w) > 3:
                tags.append(w.replace(".", "").lower())
    return tags


# this main faction those create hashtag from keyword or text
def tagss(text):  # input as string in this function
    global hashtags, glove
    hashtags = None
    if not hashtags:
        hashtags = hashtags_file()
    glove = torchtext.vocab.GloVe(name="6B", dim=50)  # trained on Wikipedia 2014 corpus

    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    stop_words = set(stopwords.words("english"))
    tag = text_to_tags(text)
    # print(tag)
    final_tags = set()
    import difflib

    precentage = 0.86
    while len(final_tags) < 30:
        for j in tag:
            x = glove[j]
            for i in hashtags:
                i = i.replace("#", "")
                # print(i, j)
                y = glove[i]
                a = torch.cosine_similarity(x.unsqueeze(0), y.unsqueeze(0))
                b = a[0].tolist()
                f = difflib.SequenceMatcher(None, j, i).ratio()

                if b > precentage:
                    if i not in stop_words:

                        final_tags.add("# " + i)
                        # print(i , b)
                if f > precentage:
                    if i not in stop_words:

                        final_tags.add("# " + i)
                        # print(i , f)
        precentage -= 0.05
        # print(len(final_tags))
    return " ".join(final_tags)


# example how can run this funtion
# print(tagss('Be your own kind of beautiful.'))
# print(tagss('beautiful'))
