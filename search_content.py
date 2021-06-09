import argparse, datetime, pymysql, re
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict
from search_keyword import search_keyword

#parser = argparse.ArgumentParser(description='Crawling Input')
#parser.add_argument('-start', required=True, help='Start Date, YYYYMMDD')
#parser.add_argument('-end', required=True, help='End Date Date, YYYYMMDD')
#parser.add_argument('-keyword', required=True, help='Searching Keyword')
#parser.add_argument('-site', required=True, help='Searching Site. naver/guru')

#args = parser.parse_args()


def _call_db_info():
    return pymysql.connect(
        host = '183.111.204.69',
        port= 13306,
        user = 'newsbot1',
        password='lgensol2020!',
        db = 'news',
        charset = 'utf8')

def clean_data(texts):
    temp = []
    for text in texts:
        #text = text.replace("·", " ").strip()
        text = text.replace('\n', ' ').strip()
        text = text.replace('\r', ' ').strip()
        pattern = '[^ ㄱ-ㅣ가-힣|0-9|a-zA-Z]+' 
        pattern2= '[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'#'[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'
        text = re.sub(pattern=pattern,  repl='', string=text)
        text = re.sub(pattern=pattern2, repl='', string=text)
        text = text.replace('  ', ' ').strip()
        text = text.lower()
        #text = kss.split_sentences(text)        
        #temp.append(str([v for v in kss.split_sentences(text)]))
        temp.append(text)
        
    return temp   

#keyword = '배터리' #s_date = '20210401' #e_date = '20210405'
def search_content(date):
    conn = _call_db_info()
    read = conn.cursor()
    tmp_sql = "select * from abstract where Date = %s and site='guru'"%date
    read.execute(tmp_sql)
    abstract = pd.DataFrame(read.fetchall())
    read.close()


    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9999")
    chrome_driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = './webdriver/chromedriver')
    
    content = []
    for i in range(0, np.shape(abstract)[0]):            
        site = abstract.iloc[i, 2]
        if site == 'guru':
            content_xpath_ = '//*[@id="news_body_area"]/p'
        elif site == 'naver':
            content_xpath_ = '//*[@id="article-view-content-div"]/p'
        
        content_url = abstract.iloc[i, 4]
        chrome_driver.get(content_url)
        chrome_driver.implicitly_wait(1)
        content_info = chrome_driver.find_elements_by_xpath(content_xpath_)

        tmp_ = []
        tmp_info = OrderedDict
        for k in range(0, len(content_info)):
            tmp_.append(content_info[k].text)
        clean_sentence = clean_data(tmp_)
        clean_sentence = [text for text in clean_sentence if len(text) > 0]
        tmp_sentence = '.'.join(clean_sentence)            

        tmp_info = OrderedDict({'id' : abstract.iloc[i, 0],
                                'date' : abstract.iloc[i, 1],
                                'site' : abstract.iloc[i, 2], 
                                'keyword' : abstract.iloc[i, 3],
                                'content' : tmp_sentence}) 
        content.append(tmp_info)
        
    content = pd.DataFrame(content)
    conn = _call_db_info()
    curs = conn.cursor()
    for i in range(0, np.shape(content)[0]):        
        tmp_id    = content['id'].loc[i]
        tmp_date  = content['date'].loc[i]
        tmp_site  = content['site'].loc[i] 
        tmp_keyword = content['keyword'].loc[i]        
        tmp_content = content['content'].loc[i]            
        tmp_insert_sql = "insert into content(Id, Date, Site, Word, Content) values('%s', '%s', '%s', '%s', '%s')"%(tmp_id, tmp_date, tmp_site, tmp_keyword, tmp_content)
        curs.execute(tmp_insert_sql)        
    conn.commit()
    conn.close()        
    print("Upload %s"%date)
    print("====================================================")
#    content.to_csv("search_content.csv", index=False, encoding="utf-8-sig")
#    print('Generate Content CSV File')
