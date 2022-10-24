from bs4 import BeautifulSoup as bs
import requests
import lxml
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys #模擬鍵盤上按鍵(以下3個)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver import ActionChains
import pandas as pd
import random
import openpyxl
from datetime import datetime, timedelta


ua = UserAgent()
user_agent = ua.random
 
options = Options()
# options.add_argument('--headless')
options.add_argument(f'user-agent={user_agent}')
options.add_argument('--disable-gpu')# Google:規避bug
options.add_experimental_option('excludeSwitches', ['enable-logging'])

def search_reddit(inputname):
    address_list = []
    url_list = []
    title_list = []
    time_list = []
    content_url = []
    content_img = []
    content_video = []

    url = f"https://www.reddit.com/search/?q={inputname}&t={time}"
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    time.sleep(5)
    js = " return action=document.body.scrollHeight " #初始化現在滾動條所在高度為0 
    height = 0#當前窗口總高度
    new_height = driver.execute_script(js)

    while height < new_height:#將滾動條調整至頁面底部
        for i in range(height, new_height, 100 ):
            driver.execute_script( ' window.scrollTo(0, {}) ' .format(i))
            time.sleep( 0.5 )
        height = new_height
        time.sleep( 2 )
        new_height = driver.execute_script(js)
    
    time.sleep(5)
    
    soup = bs(driver.page_source, 'lxml')

    # post_or_crosspost = driver.find_element(by=By.CSS_SELECTOR,value='._2fCzxBE1dlMh4OFc7B3Dun')
    for i in soup.select('div > div > div._2n04GrCyhhQf-Kshn7akmH._19FzInkloQSdrf0rh3Omen > div:nth-child(1) > div > div.y8HYJ-y_lTUHkQIc1mdCq._2INHSNB8V5eaWp4P0rY_mE > a'):
        n = i.get("href")
        addr = 'https://www.reddit.com'+ n
        address_list.append(addr)

    driver.quit()

    for url in address_list:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
        res = requests.get(url, headers=headers)
        soup = bs(res.text,'lxml')
        spl = url.split('/')
        id = spl[6]
        url2 = url + '.json'
        res2 = requests.get(url2, headers=headers).json()
        
        url_list.append(str(url))#文章網址

        unix_time = res2[0]['data']['children'][0]['data']['created']# 時間
        real_time = datetime.fromtimestamp(unix_time)
        time_list.append(str(real_time))

        # 標題
        for i in soup.select(f'#t3_{id} ._29WrubtjAcKqzJSPdQqQ4h ._eYtD2XCVieq6emjKBH3m'):
            title_list.append(i.text.replace('\n',' '))

        # 文章
        # for i in soup.select(f'#t3_{id} ._1qeIAgB0cPwnLhDF9XSiJM'):
        #     content_list.append(i.text)

        # 網址
        urll = soup.select(f'#t3_{id} ._10wC0aXnrUKfdJ4Ssz-o14')
        if len(urll) != 0:
            for i in urll:
                content_url.append(i.select_one('a').get('href'))
        else:
            content_url.append('None')

        # 圖片
        img = soup.select(f'#t3_{id} ._1NSbknF8ucHV2abfCZw2Z1', limit=2)
        if len(img) != 0:
            for i in img:
                content_img.append(i.select_one('img').get('src'))
        else:
            content_img.append('None')

        # 影片
        video = soup.select(f'#t3_{id} .m3aNC6yp8RrNM_-a0rrfa._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4._3PIKVMCKdveCEcyiKr43sU')
        if len(video) != 0:
            for i in video:
                content_video.append(i.select_one('source').get('src'))
        else:
            content_video.append('None')

    d = {}
    d['title'] = title_list
    d['url'] = url_list
    d['time'] = time_list
    d['content_url'] = content_url
    d['content_img'] = content_img
    d['content_video'] = content_video
    df = pd.DataFrame(d)
    # print(df)
    df.to_excel(inputname+'_content.xlsx', encoding="utf_8_sig")

search_reddit('Andy Lyon')
search_reddit('Injury')
