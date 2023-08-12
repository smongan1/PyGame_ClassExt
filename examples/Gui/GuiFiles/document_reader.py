# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 07:11:19 2023

@author: smong
"""
from pdfplumber import open as pdf_open
from textract import process as doc_open
from glob import glob
from os.path import join as os_join

known_extensions = {'txt', 'doc', 'docx', 'pdf'}

def read_directory_documents(path, return_page_numbers = False):
    glob_path = os_join(path,'**')
    if return_page_numbers:
        return {file : read_document_page_numbers(file) for file in glob(glob_path)}
    return {file : read_document(file) for file in glob(glob_path)}
        
def read_document(file_path, verbose = True, keep_page_numbers = False):
    ext = file_path.split('.')[-1]
    if ext not in known_extensions:
        if verbose:
            print("Unknown extension:", ext, ", skipping file", file_path)
        return None
    if keep_page_numbers: function = eval(f"read_page_numbers_{ext}")
    else: function = eval(f"read_{ext}")
    try:
        text = function(file_path)
    except:
        return None
    return text

def estimate_page_numbers(text, characters_per_page = 3000):
    text_out = []
    cnt = 1
    while text:
        t = text[:characters_per_page].strip()
        if t: text_out.append([cnt, t])
        cnt += 1
    return text_out

def read_txt(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    return text

def read_page_numbers_txt(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    estimated = True
    return estimate_page_numbers(text), estimated


def read_pdf(file_path):
    text = ''
    with pdf_open(file_path) as pdf:    
       text = pdf.pages[0].extract_text()
       for page in pdf.pages[1:]:
           text = '\n'.join([text, page.extract_text()])
    return text

def read_page_numbers_pdf(file_path):
    text = ''
    with pdf_open(file_path) as pdf:    
       text = [[i + 1, x.extract_text()] for i,x in enumerate(pdf.pages)]
    estimated = False
    return text, estimated

def read_doc(file_path):
    return doc_open(file_path)
    
def read_docx(file_path):
    return doc_open(file_path)