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


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9999")
chrome_driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = './webdriver/chromedriver')

try:
    chrome_driver.get("https://news.naver.com")
    keyword = '배터리'
    s_date = '20210401'
    e_date = '20210405'
    start = str(s_date)[0:4]+'.'+str(s_date)[4:6]+'.'+str(s_date)[6:]    
    end = str(e_date)[0:4]+'.'+str(e_date)[4:6]+'.'+str(e_date)[6:]    
    print(start, " ~ ", end)

    naver_url = 'https://search.naver.com/search.naver?where=news&query={}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={}&de={}&docid=&related=0&mynews=1&office_type=2&office_section_code=8&news_office_checked=2598&nso=so%3Ar%2Cp%3Afrom{}to{}'.format(keyword, start, end,s_date, e_date)
    #title_path = "//div[@class='article-head-title']"
    #date_path = '//div[@class="info-text"]'
    #body_path = '//*[@id="article-view-content-div"]'
    #//*[@id="sp_nws1"]/div/div/a
    
    print(chrome_driver.current_url)
    chrome_driver.get(naver_url)
    chrome_driver.implicitly_wait(1)
    test_info = chrome_driver.find_elements_by_xpath('//*[@id="sp_nws1"]/div/div/div[2]/div/a')#    
    soup = BeautifulSoup(req, 'html.parser')
    print(sour)
    #test_info.click()
    #print(chrome_driver.current_url)
    #req = chrome_driver.page_source
    #soup = BeautifulSoup(req, 'html.parser')
    #print(soup)
    # lis = elem.find_elements_by_class_name('hdline_article_tit')   
    #for li in list:
    #    print(li.text)

except Exception as e:
    print(e)
finally:
    chrome_driver.quit()