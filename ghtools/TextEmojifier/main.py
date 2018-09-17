# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import random
from unidecode import unidecode
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
wordnet_lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("spanish")


pattern = r"""(?x)                            # set flag to allow verbose regexps
              (?:[a-zA-Z]\.)+                 # abbreviations, e.g. U.S.A.
              |[a-zA-Z]+(?:[-'*][a-zA-Z]+)*   # words w/ optional internal hyphens/apostrophe
              |[0-9]+                         # numbers
            """
tokenizer = nltk.RegexpTokenizer(pattern)




def clean_text(text, full=True):
    tokens = text.split(' ')
    tokens_clean = []
    for token in tokens:
        token = token.lower()
        if full:
            token = token if token not in stopwords else ''
            token = tokenizer.tokenize(token)[0] if tokenizer.tokenize(token) != [] else ''
        token = unidecode(token)
        if full:
            # token = stemmer.stem(token)
            token = wordnet_lemmatizer.lemmatize(token) 
        tokens_clean.append(token)
    return ' '.join(filter(None, tokens_clean))


stopwords_path = "stopwords_es.txt"
with open(stopwords_path, "r") as file:
    stopwords = file.read().splitlines()
    stopwords = [clean_text(s, False) for s in stopwords]


df_emojis = pd.read_csv('emojis_clean_mod.csv')
df_emojis_unique = pd.read_csv('emojisu_clean_mod.csv') # especial emojis like country names
df_emojis['es'] = df_emojis['es'].apply(lambda x: clean_text(x))
df_emojis_unique['es'] = df_emojis_unique['es'].apply(lambda x: clean_text(x, full=False))

# df_emojis = pd.concat([df_emojis, df_emojis_unique])

df_emojis = df_emojis.groupby('es')['alt'].apply(list).to_dict()
df_emojis_unique = df_emojis_unique.groupby('es')['alt'].apply(list).to_dict()


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

for key in list(df_emojis.keys()):
    strings = []
    strings.extend(key.split(' '))
    for s in strings:
        if s in df_emojis.keys():
            if df_emojis[key][0] not in df_emojis[s]:
                df_emojis[s].append(df_emojis[key][0])
        else:
            df_emojis[s] = df_emojis[key]

df_emojis = merge_two_dicts(df_emojis, df_emojis_unique)


def get_emoji(token):
    if token not in df_emojis:
        return ''
    return random.choice(df_emojis[token])






with open('input.txt') as f:
    input_text = f.readlines()
inputs = ''.join(input_text)

processed = []

words = inputs.split(' ')
for word in words:
    token = clean_text(word)
    emoji = get_emoji(token)
    if emoji is '':
        processed.append(word)
    else:
        # print(word)
        if '.' in word:
            word = word.replace('.', ' {}.'.format(emoji), 1)
            processed.append(word)
        elif ',' in word:
            word = word.replace(',', ' {},'.format(emoji), 1)
            processed.append(word)
        elif '\n' in word:
            word = word.replace('\n', ' {}\n'.format(emoji), 1)
            processed.append(word) 
        else:
            processed.append(word)
            processed.append(emoji)

# print(df_emojis['']) # this should be always empty

# Rejoin
output = ' '.join(processed)

text_file = open("output.txt", "w")
text_file.write(output)
text_file.close()

