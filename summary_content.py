import os, re, kss
import numpy as np
import pandas as pd
import torch
from torch import nn, optim
import torch.nn.functional as F
import datetime, pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict

import transformers
from transformers import BertTokenizerFast, EncoderDecoderModel
from pororo import Pororo
from LMKor.examples.bertshared_summarization import Summarize
from article_class import classifier

class Summarize():    
    def __init__(self, model_name, device):
        self.tokenizer = BertTokenizerFast.from_pretrained(model_name)
        self.model = EncoderDecoderModel.from_pretrained(model_name)
        self.model = self.model.to(device)

    def __call__(self, text):
        input_ids = self.tokenizer.encode(text, return_tensors='pt')
        input_ids = input_ids.to(device)

        sentence_length = len(input_ids[0])
        min_length = max(10,  int(0.1*sentence_length))
        max_length = min(512, int(0.3*sentence_length))

        sentence_length = torch.tensor(sentence_length)
        min_length = torch.tensor(min_length)
        max_length = torch.tensor(max_length)

        outputs = self.model.generate(
            input_ids, min_length = min_length, max_length = max_length).to(device)
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens = True)
        return str(result)
    
def clean_data(texts):
    temp = []
    for text in texts:
        #text = text.replace("·", " ").strip()
        text = text.replace('\n', ' ').strip()
        text = text.replace('\r', ' ').strip()
        pattern = '[^ ㄱ-ㅣ가-힣|0-9|a-zA-Z]+' 
        pattern2= '[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'
        text = re.sub(pattern=pattern,  repl='', string=text)
        text = re.sub(pattern=pattern2, repl='', string=text)
        text = text.replace('  ', ' ').strip()
        text = text.lower()
        #text = kss.split_sentences(text)        
        #temp.append(str([v for v in kss.split_sentences(text)]))
        temp.append(text)        
    return temp

def clean_sentence(texts):
    pattern = '[^ ㄱ-ㅣ가-힣|0-9|a-zA-Z]+' 
    pattern2= '[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'
    #text = re.sub(pattern=pattern,  repl='', string=text)
    texts1 = re.sub(pattern=pattern2, repl='', string=texts)
    return texts1


def _call_db_info():
    return pymysql.connect(
        host = '183.111.204.69',
        port= 13306,
        user = 'newsbot1',
        password='lgensol2020!',
        db = 'news',
        charset = 'utf8')

def chunk(l, n):
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        yield l[si:si+(d+1 if i < r else d)]
        
def summary_content(date):
    print("Upload %s"%date)
    conn = _call_db_info()
    read = conn.cursor()
    tmp_sql = "select * from content where Date = %s and site='guru'"%date
    read.execute(tmp_sql)
    content = pd.DataFrame(read.fetchall())
    read.close()

    if np.shape(content)[0] > 0 :
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        #tokenizer = BertTokenizerFast.from_pretrained('./bertshared-kor-base/')
        #bertshared_abs = Summarize('./bertshared-kor-base/', device)
        #pororo_ext   = Pororo(task='summary', model='extractive', lang='ko')
        pororo_abs   = Pororo(task='summary', model='abstractive', lang='ko')
        #pororo_bullet= Pororo(task='summary', model='bullet', lang='ko')

        #len(tmp_sentence)
        #rslt_bert_abs = bertshared_abs(tmp_sentence)
        #rslt_poro_ext = pororo_ext(tmp_sentence)
        #rslt_poro_abs = pororo_abs(tmp_sentence)
        #rslt_poro_bul = pororo_bullet(tmp_sentence)

        infer = []
        for i in range(0, np.shape(content)[0]):
            tmp_id = content.iloc[i, 0]
            tmp_date = content.iloc[i, 1]
            tmp_site = content.iloc[i, 2]
            tmp_keyword = content.iloc[i, 3]
            tmp_content = content.iloc[i, 4]

            sent_split = kss.split_sentences(tmp_content)
            n_of_div = (len(tmp_content) // 3000) + 1
            tmp_summary = []
            for p in chunk(sent_split, n_of_div):
                temp_ = ''
                for s in p:
                    temp_ += s
                    temp_ += ' '
                tmp_summary.append(clean_sentence(pororo_abs(temp_)))
            tmp_summary = ''.join(tmp_summary)  
            #tmp_class = classifier(tmp_summary)

            #if tmp_keyword in ['LG에너지솔루션']:
            #    tmp_label = 0  # 자사
            #elif tmp_keyword in ['삼성SDI', 'SK이노베이션', 'CATL']:
            #    tmp_label = 1  # 경쟁사
            #elif tmp_keyword in ['현대차', 'BMW', 'GM']:
            #    tmp_label = 2  # 고객사
            #elif tmp_keyword in ['배터리', '전고체']:
            #    tmp_label = 3  # 산업/기술    

            tmp_info = OrderedDict({'id' : content.iloc[i, 0],
                                    'date' : content.iloc[i, 1],
                                    'site' : content.iloc[i, 2], 
                                    'keyword' : content.iloc[i, 3],
                                    'content' : tmp_summary})#,
                                    #'label' : tmp_label}) 
            infer.append(tmp_info)     
        infer = pd.DataFrame(infer)
        tmp_label = classifier(infer['content'])

        conn = _call_db_info()
        curs = conn.cursor()
        for i in range(0, np.shape(infer)[0]):        
            tmp_id    = infer['id'].loc[i]
            tmp_date  = infer['date'].loc[i]
            tmp_site  = infer['site'].loc[i] 
            tmp_keyword = infer['keyword'].loc[i]        
            tmp_summary = infer['content'].loc[i]            
            tmp_class = tmp_label[i]#infer['label'].loc[i]            
            tmp_insert_sql = "insert into infer(Id, Date, Site, Word, Summary, Label) values('%s', '%s', '%s', '%s', '%s', '%s')"%(tmp_id, tmp_date, tmp_site, tmp_keyword, tmp_summary, tmp_class)
            #print(tmp_insert_sql)
            curs.execute(tmp_insert_sql)        
        conn.commit()
        conn.close()     
    
    print("====================================================")    