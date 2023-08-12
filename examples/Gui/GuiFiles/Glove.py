# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 07:28:40 2023

@author: smong
"""
import re
from sentence_tools import stopwords_bytes, normalize_text
import numpy as np
from sklearn.cluster import KMeans
import os

def is_number(x):
    x = x.strip()
    return re.sub(b'[a-zA-Z]',b'', x[:1]) == x[:1]

def reformatDirConfig(dir_config):
    dir_config = dir_config.split('\\')
    if len(dir_config) == 1:
        dir_config = dir_config[0].split('/')
    dir_config = [x for x in dir_config if x]
    dir_config = os.path.abspath(os.path.join(*dir_config))
    return dir_config.replace('"', '').replace("'", '').strip()

def read_configs():
    dir_config_labels = ['\\', '/']
    loc = os.path.dirname(__file__)
    conf_path = os.path.join(loc, 'configuration.conf')
    with open(conf_path, 'r') as f:
        data = f.read()
    config_dictionary = dict([[x.strip() for x in line.split('=')] for line in data.split('\n') if not line.strip()[0] == '#'])
    for x in config_dictionary:
        if '_file' in x:
            config_dictionary[x] = reformatDirConfig(config_dictionary[x])
    return config_dictionary

class GLOVE():
    def __init__(self, configs):
        self.vecs = {}
        if 'vector_file' in configs:
            self.vecs = read_vecs(configs['vector_file'])
            temp_vec = self.vecs.popitem()
            self.vecs[temp_vec[0]] = temp_vec[1]
            self.vec_len = len(temp_vec[1])
            self.use_library = False
        else:
            self.library = configs['library']
            dirs = os.listdir(self.library)[0]
            vec_file = os.listdir(os.path.join(self.library, dirs))[0]
            vec_file = os.path.join(self.library, dirs, vec_file)
            with open(vec_file, 'r') as f: data = f.read()
            self.vec_len = len(data.split(','))
            self.use_library = True
        self.keys = [x for x in self.vecs]
        
    def get_vector(self, text):
        text = normalize_text(text)
        vector = np.zeros(self.vec_len)
        for word in text:
            if not word in self.vecs:
                if not self.use_library: continue
                status = self.get_word_vector(word)
                if not status: continue
            vector += self.vecs[word]
        return vector
    
    def get_word_vector(self, word):
        ref_file = os.path.join(self.library,word[0], word)
        if os.path.isfile(ref_file):
            with open(ref_file) as f: data = f.read()
            data = data.strip()
            self.vecs[word] = np.array([float(x) for x in data.split(',')])
            return 1
        return 0
    
def read_vecs(file):
    with open(file, 'rb') as f:
        data = f.read()
    data = data.split(b'\n')
    words = []
    vecs = np.zeros((len(data), len(data[0].split(b' ')) - 1))
    for i, line in enumerate(data):
        if len(line) < 100: continue
        if not line: break
        line = line.split(b' ')
        word = line[0]
        line = line[1:]
        if word in stopwords_bytes or len(word) < 3 or not re.sub(b'[^a-z^A-Z]',b'',word): 
            continue
        vecs[i, :] = [float(x) for x in line]
        words.append(word)
    return {x[0] : x[1] for word, vec in zip(words, vecs) for x in [[word.decode(),vec], [word , vec]]}

def cosine_similarity(vec1, vec2):
    norm1 = np.linalg.norm(vec1)
    if norm1 == 0: return 0
    norm2 = np.linalg.norm(vec2)
    if norm2 == 0: return 0
    return np.dot(vec1, vec2)/(norm1*norm2)

def item_distance(vector1, vector2, text1, text2):
    text1 = re.sub('[^a-z^A-Z^0-9]', ' ', text1).lower()
    set1 = {x for x in text1.split(' ') if x}
    text2 = re.sub('[^a-z^A-Z^0-9]', ' ', text2).lower()
    set2 = {x for x in text2.split(' ') if x}
    if len(set1) == 0 or len(set2) == 0: return 0
    sim = cosine_similarity(vector1, vector2)
    inter = len(set1.intersection(set2))/(len(set1)+len(set2))
    return inter * sim

def item_distance2(vector1, vector2, text1, text2):
    text1 = re.sub('[^a-z^A-Z^0-9]', ' ', text1).lower()
    set1 = {x for x in text1.split(' ') if x}
    text2 = re.sub('[^a-z^A-Z^0-9]', ' ', text2).lower()
    set2 = {x for x in text2.split(' ') if x}
    mlen = min(len(set1), len(set2))
    if len(set1) == 0 or len(set2) == 0: return 0
    sim = cosine_similarity(vector1, vector2)
    inter = len(set1.intersection(set2))/mlen
    return inter*(sim**4 + 1)/2

def build_library(vecs, loc):
    if not os.path.isdir(loc):
        os.mkdir(loc)
    failed_words = []
    keys = [x for x in vecs]
    for word in keys:
        if re.sub(r'[\/]', '' ,word) != word:
            print(word)
            continue
        letter = word[0]
        path = os.path.join(loc, letter)
        if not os.path.isdir(path):
            os.mkdir(path)
        path = os.path.join(path, word)
        vector_str = ','.join([str(y) for y in vecs[word]])
        try: 
            with open(path, 'w') as f: f.write(vector_str)
        except:failed_words.append(word)
    return failed_words
configs = read_configs()
glove = GLOVE(configs)

