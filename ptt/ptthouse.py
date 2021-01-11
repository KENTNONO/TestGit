import requests
import os
import logging
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import random
import urllib

logging.basicConfig(filename='./log/ptt.log' ,level=logging.ERROR,format='%(asctime)s:%(levelname)s:%(message)s')

driverPath = './geckodriver'
browser = webdriver.Firefox(executable_path=driverPath)

headers ={
    'Host':'pttcareers.com',
    'Referer':'https://pttcareers.com/home-sale/page',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

def ptt_selium_page_list():
    all_res = []
    response = {}
    ss = requests.session()
    ss.headers.update(headers)
    url = 'https://pttcareers.com/home-sale/page'
    total_count = 1000
    count = 0
    file_count = 1
    need_check = 0
    while True:
        try:
            browser.get(url)
            time.sleep(random.randrange(1,3))
            next_page=browser.find_elements_by_xpath('//*[@class="blue darken-3 v-btn v-btn--router v-btn--small theme--dark"]')

            url=next_page[1].get_attribute('href')
            parsing=urllib.parse.urlparse(url)
            print(parsing)

            if (not (file_count == 1 and count == 0)) and (need_check-25)!=int(urllib.parse.parse_qs(parsing[4])['n'][0]):
                logging.error('PAGE ERROR')
            need_check=int(urllib.parse.parse_qs(parsing[4])['n'][0])
            list_pages=browser.find_elements_by_xpath('//a[@class="e7-article-default"]')
            random.shuffle(list_pages)
            for i in list_pages:
                try:
                    res = ss.get(i.get_attribute('href'))
                    soup = BeautifulSoup(res.text,'html.parser')
                    response['url'] = i.get_attribute('href')
                    response['title']=soup.find('title').getText()
                    response['main']=soup.find(attrs={'itemprop':'articleBody'}).getText()
                    response['recovery']=list(i.getText() for i in soup.find_all(attrs={'itemprop':'text'}))
                    response['createTime']=soup.find('time').getText()
                    all_res.append(response)
                    response = dict()
                    # time.sleep(random.randrange(1,2))
                except :
                    logging.error('craby error:' + i.get_attribute('href'), exc_info=True)

                count+=1
            if count%100==0:
                time.sleep(random.randrange(5, 6))
            if count>=total_count:
                try:

                    with open ('./data/ptt/download_'+str(file_count)+'.json','w',encoding='utf-8') as f:
                        json.dump({'allList':all_res},f,ensure_ascii=False)
                    file_count += 1
                    count = 0
                    all_res=[]
                except :
                    with open ('./data/ptt/downloaderror_'+str(file_count)+'.txt','w',encoding='utf-8') as f:
                        f.write(str(all_res))
                        logging.error('batch export error' + str(file_count), exc_info=True)
                    file_count += 1
                    count = 0
                    all_res=[]
            if need_check==4000:
                break
            logging.debug(url+':'+str(file_count))
        except :
            logging.error(url+':'+str(file_count))
    try:    
        with open ('./data/ptt/download_'+str(file_count)+'.json','w',encoding='utf-8') as f:
            json.dump({'allList'+str(file_count):all_res},f,ensure_ascii=False)
            logging.debug('sucess' + str(file_count))
    except :
        with open ('./data/ptt/downloaderror_'+str(file_count)+'.txt','w',encoding='utf-8') as f:
            f.write(str(all_res))
            logging.error('batch export error' + str(file_count), exc_info=True)


if __name__ == "__main__":
    ptt_selium_page_list()