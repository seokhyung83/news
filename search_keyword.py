## Chrome 설치 및 안내 : 
## 1) https://jh-industry.tistory.com/m/14
## 
## Selenium Documents
## 1) https://selenium-python.readthedocs.io/index.html
##
## BeautifulSoup
## 1) ...

from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict
import pandas as pd
import numpy as np
import pymysql, re

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9999")
chrome_driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = './webdriver/chromedriver')
chrome_driver.get("https://news.naver.com")

def _call_db_info():
    return pymysql.connect(
        host = '183.111.204.69',
        port= 13306,
        user = 'newsbot1',
        password='lgensol2020!',
        db = 'news',
        charset = 'utf8')


def search_keyword(date):
    conn = _call_db_info()
    read = conn.cursor()
    tmp_sql = "select * from word_dic where Site='guru'"
    read.execute(tmp_sql)
    word_dic = pd.DataFrame(read.fetchall())
    read.close()
    print("Date %s"%date)
    candidate_info = []
    for w in range(0, np.shape(word_dic)[0]):
        keyword = word_dic.iloc[w, 2]
        site = word_dic.iloc[w, 1]
        if site == 'guru':
            start = str(date)[0:4]+'-'+str(date)[4:6]+'-'+str(date)[6:]                
            url_ = 'https://theguru.co.kr/news/search_result.html?search_mode=multi&s_title=1&search={}&s_sdate={}&s_edate={}&catno='.format(keyword, start, start)
            page_xpath_  = '//div[@class="btn_pagenum"]/a'
            table_xpath_ = '//ul[@class="art_list_all"]'
            list_xpath_  = './li'
            url_xpath_ = './a'  ##      dsc_xpath_ = './a/p'        news_info_xpath_ = './a/ul/li[2]'
            title_xpath_ = './a/h2'

        elif site == 'naver':
            start = str(date)[0:4]+'.'+str(date)[4:6]+'.'+str(date)[6:]                       
            url_ = 'https://search.naver.com/search.naver?where=news&query={}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={}&de={}&docid=&related=0&mynews=1&office_type=2&office_section_code=8&news_office_checked=2598&nso=so%3Ar%2Cp%3Afrom{}to{}'.format(keyword,start,start,date,date)
            page_xpath_  = '//div[@class="sc_page_inner"]/a'
            table_xpath_ = '//ul[@class="list_news"]'
            list_xpath_  = './li[contains(@id, "sp_nws")]/div/div'
            url_xpath_ = './a'  ##       dsc_xpath_ = './div[2]'      news_info_xpath_ = './div[1]/div/span'
            title_xpath_ = './a'

        chrome_driver.get(url_)
        search_rslt_url = []
        pagenum = chrome_driver.find_elements_by_xpath(page_xpath_)
        cnt = 0
        for i in pagenum:
            search_rslt_url.append(pagenum[cnt].get_attribute('href'))
            cnt+=1

        can_len_old = len(candidate_info)
        for i in search_rslt_url:
            try:
                chrome_driver.get(i)
                chrome_driver.implicitly_wait(3)
                table = chrome_driver.find_element_by_xpath(table_xpath_)
                li_list = table.find_elements_by_xpath(list_xpath_)      

                for li_id in range(0, len(li_list)):
                    tmp_info = OrderedDict()
                    tmp_url = li_list[li_id].find_element_by_xpath(url_xpath_)
                    #tmp_dsc = li_list[li_id].find_element_by_xpath(dsc_xpath_)
                    #tmp_news_info = li_list[li_id].find_element_by_xpath(news_info_xpath_)
                    tmp_title = li_list[li_id].find_element_by_xpath(title_xpath_)
                    tmp_info = OrderedDict({'date' : date,
                                            'site' : site,
                                            'keyword' : keyword,                                            
                                            'url' : tmp_url.get_attribute('href'),                                            
                                            'title' : tmp_title.text})
                    candidate_info.append(tmp_info)        
            except:
                pass
        if len(candidate_info)-can_len_old > 0:
            print("Searching %s in %s and Find # of %d articles"%(keyword, site, len(candidate_info)-can_len_old))

    candidate_info = pd.DataFrame(candidate_info)#['date']
    conn = _call_db_info()
    curs = conn.cursor()
    for i in range(0, np.shape(candidate_info)[0]):
        pattern= '[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'    
        tmp_date    = candidate_info['date'].loc[i] #pd.to_datetime(candidate_info['date'].loc[i]).strftime('%Y%m%d')
        tmp_site    = candidate_info['site'].loc[i] 
        tmp_keyword = candidate_info['keyword'].loc[i]
        tmp_url     = candidate_info['url'].loc[i]
        tmp_title   = candidate_info['title'].loc[i]    
        tmp_title = re.sub(pattern=pattern, repl='', string=tmp_title)
        tmp_insert_sql = "insert into abstract(Date, Site, Word, Url, Title) values('%s', '%s', '%s', '%s', '%s')"%(tmp_date, tmp_site, tmp_keyword, tmp_url, tmp_title)
        curs.execute(tmp_insert_sql)        
    conn.commit()
    conn.close()
    print("====================================================")