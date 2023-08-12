# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 17:44:50 2023

@author: smong
"""

from copy import deepcopy
from sentence_tools import split_into_sentences, normalize_text
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from Glove import glove, cosine_similarity, item_distance, item_distance2
from document_reader import read_document
import numpy as np
from threading import Thread
import os
import time

class ReadDocumentThread(Thread):
    def run(self):
        self.document = None
        self.failed = False
        text = read_document(self.file, verbose = False, keep_page_numbers = True)
        if not text:
            self.failed = True
            return
        name = self.file.split('/')[-1].split('.')[0]
        self.document = Document(text, 
                                 text_display_limit = self.text_display_limit, 
                                 name = name)
        self.document.file = self.file
        print(self.file)
        
class ReadDocumentThreadPool():
    def __init__(self, files, text_display_limit, n_threads = 8):
        n_threads = min(n_threads, len(files))
        self.threads = [None for x in range(n_threads)]
        
        self.files = files
        self.text_display_limit = text_display_limit
        self.documents = []
        self.failed_extensions = []
        
    def run(self):
        files = [x for x in self.files]
        while files:
            self.start_new_threads(files)
            time.sleep(0.01)
        for thread in self.threads:
            self.collect_document(thread)

    def start_new_threads(self, files):
        for i, thread in enumerate(self.threads):
            if thread and thread.is_alive():
                continue
            self.collect_document(thread)
            if files:
                file = files.pop()
                thread = self.start_new_thread(file)
                self.threads[i] = thread
                
    def collect_document(self, thread):
        if thread and not thread.joined:
            thread.join()
            if thread.failed:
                ext = os.path.split(thread.file)[-1].split('.')[-1]
                self.failed_extensions.append(ext)
            thread.joined = True
            self.documents.append(thread.document)
    
    def start_new_thread(self, file):
        thread = ReadDocumentThread()
        thread.text_display_limit = self.text_display_limit
        thread.joined = False
        thread.file = file
        thread.start()
        return thread

class Case():
    def __init__(self, document_files, text_display_limit = 200, 
                 min_search_results = 10, average_bin_size = 25):
        self.documents = []
        self.document_index_dictionary = {}
        self.text_display_limit = text_display_limit
        self.average_bin_size = average_bin_size
        self.min_search_results = min_search_results
        self.sentences = []
        self.failed_extensions = set()
        # for file in document_files:
        #     self.add_document(file)
        self.add_documents_multi(document_files)
        if self.failed_extensions:
            print("The following file types failed to load")
            print(self.failed_extensions)
        self.bin_vectors()
        
    def add_document(self, file):
        text = read_document(file, verbose = False)
        if not text:
            self.failed_extensions.add(file.split('.')[-1])
            return
        name = file.split('/')[-1].split('.')[0]
        document = Document(text, text_display_limit = self.text_display_limit, name = name)
        document.case = self
        self.document_index_dictionary[name] = len(self.documents)
        self.documents.append(document)
        self.sentences.extend(document.sentences)
        
    def add_documents_multi(self, files):
        thread_runner = ReadDocumentThreadPool(files, self.text_display_limit)
        thread_runner.run()
        self.failed_extensions = thread_runner.failed_extensions
        for i, document in enumerate(thread_runner.documents):
            document.case = self
            self.document_index_dictionary[document.name] = len(self.documents)
            self.documents.append(document)
            self.sentences.extend(document.sentences)
        
    def get_sorted_labels(self, vector):
        labels = {'sentences' : None, 'documents' : None}
        for lab_type in labels:
            lab_dis = self.kmeans[lab_type].transform(vector)
            lab_dis = [[label, dist] for label, dist in enumerate(lab_dis)]
            lab_dis = sorted(lab_dis, key = (lambda x: x[1]))
            labels[lab_type] = [x[0] for x in lab_dis]
        return labels
    
    def get_vector_bin_items_kmeans(self, vector):
        bin_items = {}
        sorted_labels = self.get_sorted_labels(vector)
        for label_type in sorted_labels:
            sort_lab = sorted_labels[label_type]
            bin_item_tmp = []
            for label in sort_lab:
                if len(bin_item_tmp) > self.min_search_results: break
                bin_item_tmp.extend(self.bins[label_type][label])
            bin_items[label_type] = bin_item_tmp
        return bin_items
    
    def get_vector_bin_items(self, vector):
        bin_items = {}
        for label_type in self.knn:
            datas = self.__getattribute__(label_type)
            n_neghbors = min(self.min_search_results, 
                             len(datas),
                             self.knn[label_type].n_samples_fit_)
            neighbors = self.knn[label_type].kneighbors(vector, n_neghbors, 
                                                        return_distance=False)
            bin_items[label_type] = [datas[x] for x in neighbors[0]]
        return bin_items
    
    def get_closest_items(self, vector, text):
        bin_items = self.get_vector_bin_items(vector.reshape(1, -1))
        for label_type in bin_items:
            bin_items[label_type] = sorted(bin_items[label_type],
                                           key = lambda x: 
                                           item_distance(x.vector, vector, x.text, text),
                                           reverse = True)
        return bin_items
    
    def bin_vectors_kmeans(self):
        num_sentence_bins = len(self.sentences)//self.average_bin_size + 1
        num_document_bins = len(self.documents)//self.average_bin_size + 1

        self.kmeans = {'sentences' : KMeans(n_clusters = num_sentence_bins),
                        'documents' : KMeans(n_clusters = num_document_bins)}
        
        self.bins = {}
        for label_type in self.kmeans:
            items = [x for x in self.__getattribute__(label_type) if hasattr(x.vector,'__iter__')]
            item_labels = self.kmeans[label_type].fit_predict([x.vector for x in items])
            self.bins[label_type] = {x: [] for x in set(item_labels)}
            for label, item in zip(item_labels, items):
                self.bins[label_type][label].append(item)
    
    def bin_vectors(self):
        
        self.knn = {'sentences' : NearestNeighbors(
                            n_neighbors = self.min_search_results, 
                            metric = 'cosine'),
                        'documents' : NearestNeighbors(
                            n_neighbors =  self.min_search_results, 
                            metric = 'cosine')}
        self.bins = {}
        for label_type in self.knn:
            items = [x for x in self.__getattribute__(label_type) if hasattr(x.vector,'__iter__')]
            self.knn[label_type].fit([x.vector for x in items])
    
    def get_vec(self, text):
        return glove.get_vector(text)
    
    def search(self, text = None):
        word_vectors = self.get_vec(text)
        norm = np.linalg.norm(word_vectors)
        if norm:
            word_vectors = word_vectors/norm
        return self.get_closest_items(word_vectors, text)
        
                
class Document():
    def __init__(self, text, text_display_limit = 200, name = None):
        self.text = ''
        self.name = name
        self.case = None
        self.sentences = []
        self.sentence_index_dictionary = {}
        for page_number, text in text[0]:
            self.add_page(page_number, text, text[1])
        self.vector = sum([x.vector for x in self.sentences])
        if len(self.sentences):
            self.vector = self.vector/len(self.sentences)
        self.text_display_limit = text_display_limit
        
    def get_display_sentence(self, sentence_index = None, text = None):
        if not text is None:
            sentence_index = self.get_sentence_index_from_text(text)
        display_text = ''
        if sentence_index != 0:
            display_text = self.get_displayable_sentence(sentence_index, -1) + ' '
        display_text += self.sentences[sentence_index].text
        if sentence_index != len(self.sentences)-1:
            display_text += ' ' + self.get_displayable_sentence(sentence_index, 1)
        return display_text
    
    def add_page(self, page_number, page_text, is_estimate_page_count):
        sentences = split_into_sentences(page_text)
        if not sentences: 
            sentences = page_text.split('\n')
        self.add_sentences(sentences, page_number, is_estimate_page_count)
        self.text += page_text
    
    def add_sentences(self, sentences, page_number, is_estimate_page_count):
        for sentence in sentences:
            self.add_sentence(sentence, page_number, is_estimate_page_count)
            
    def add_sentence(self, sentence, page_number, is_estimate_page_count):
        sentence = Sentence(sentence)
        sentence.page_number = page_number
        sentence.is_estimate_page_count = is_estimate_page_count
        sentence.document = self
        sentence_index = len(self.sentences)
        self.sentence_index_dictionary[sentence] = sentence_index
        sentence.index = sentence_index
        self.sentences.append(sentence)
        
    def get_sentence_index_from_text(self, text):
        if text in self.sentence_index_dictionary:
            return self.sentence_index_dictionary[text]
        
    def get_displayable_sentence(self, sentence_index, offset):
        sentence_text = self.sentences[sentence_index + offset].text
        if len(sentence_text) <= self.text_display_limit + 3:
            return sentence_text
        if offset < 0:
            sentence_text = '...' + sentence_text[-(self.text_display_limit):]
        else:
            sentence_text = sentence_text[:self.text_display_limit] + '...'
        return sentence_text
    
    def get_displayable_text(self):
        return self.name
    
    def score(self, text):
        vec = self.case.get_vec(text)
        return item_distance2(self.vector, vec, self.text, text)
    
    def score2(self, text):
        val = sum([x.sim(text) > 0.01 for x in self.sentences])/len(self.sentences)
        return (val + 1)/2
    
    def score3(self, text):
        if not len(self.sentences):
            return 0
        vals = [i for i, x in enumerate(self.sentences) if x.sim(text) > 0.005]
        if len(vals) < 4:
            return sum([x.score(text) > 0.505
                        for x in self.sentences])/len(self.sentences)
        ratio1 = np.log(len(vals))/np.log(len(self.sentences))
        ratio2 = 1 - np.std(vals)/(max(vals) - min(vals))
        val =  ratio1**3 * ratio2**.75
        return val
    
class Sentence():
    def __init__(self, text):
        self.text = text
        self.vector = glove.get_vector(text)
        norm = np.linalg.norm(self.vector)
        if norm:
            self.vector = self.vector/norm
        self.index = None
        self.document = None
        
    def get_displayable_text(self):
        if self.document:
            return self.document.get_display_sentence(sentence_index = self.index)
        return self.text
    
    def score(self, text):
        vec = self.document.case.get_vec(text)
        return item_distance(self.vector, vec, self.text, text)
    
    def sim(self, text):
        vec = self.document.case.get_vec(text)
        return cosine_similarity(self.vector, vec)