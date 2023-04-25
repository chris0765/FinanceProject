from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import datetime
import time
import os
import pickle5 as pickle

CRAWL_URL_BASIC = "https://finance.naver.com/item/news_news.nhn"
COMPANY_CODE_URL = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201"

HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

PATH = os.getcwd() + os.path.sep
DATA_PATH = PATH+"data"+os.path.sep

COMPANY_CODES = None

for filename in os.listdir(DATA_PATH):
    if 'data' in filename.split('/')[-1] and 'crdownload' not in filename.split('/')[-1]:
        COMPANY_CODES = pd.read_csv(DATA_PATH+filename, encoding='cp949').reset_index(drop=True)
        break

if COMPANY_CODES is None:
    print("[ERROR]Company Code Is Empty.")
    exit()

news_list = None
saved_index = None
try:
    saved_index, news_list, collected_text = pickle.load(open(DATA_PATH+"saved_news.pkl", "rb"))
except:
    saved_index, news_list, collected_text = (-1, [], 0)
prevText = collected_text

for idx, row in COMPANY_CODES.iterrows():
    if idx <= saved_index:
        continue
    COMPANY_CODE = row["단축코드"]
    COMPANY_NAME = row["한글 종목약명"]
    print(f"News about '{COMPANY_NAME}' is now crawling({idx+1}/{len(COMPANY_CODES)})...{(idx+1)*100//len(COMPANY_CODES)}%")
    print(f"\tGet Recent News URL About '{COMPANY_NAME}'")

    pageIndex = 1
    new_list = []

    while True:
        newsUrl = CRAWL_URL_BASIC+f"?code={COMPANY_CODE}&page={pageIndex}"
        now = datetime.datetime.strptime(time.strftime("%Y.%m.%d %H:%M", time.localtime(time.time())), "%Y.%m.%d %H:%M")
        
        response = requests.get(newsUrl, headers=HEADERS)
        html = bs(response.text, 'html.parser')
        trs = html.select("body > div > table.type5 > tbody > tr")
        navis = html.select("body > div > table.Nnavi > tr > td")
        
        numButtons = 0
        nextButton = False

        for navi in navis:
            try:
                if 'pgLL' in navi['class'] or 'pgL' in navi['class'] or 'pgRR' in navi['class']:
                    continue
                elif 'pgR' in navi['class']:
                    nextButton = True
                    continue
            except:
                pass
            numButtons += 1
        
        if pageIndex%10==0 and nextButton is False:
            break

        if numButtons < pageIndex%10:
            break

        for tr in trs:
            try:
                if 'relation_lst' in tr['class']:
                    continue
            except:
                pass
            if len(tr.select("div[class='info_text_area']")):
                now = None
                break
            news_dict = {"단축코드":COMPANY_CODE, "한글 종목약명":COMPANY_NAME}
            news_dict['제목'] = tr.select_one('.title').get_text().strip()
            news_dict['URL'] = 'https://finance.naver.com' + tr.select_one('.title').find('a')['href']
            news_dict['날짜'] = tr.select_one('.date').get_text().strip().split(' ')[0]
            news_dict['정보제공'] = tr.select_one('.info').get_text().strip()
            date = datetime.datetime.strptime(news_dict["날짜"], "%Y.%m.%d")
            if (now-date).days > 100:
                now = None
                break
            new_list.append(news_dict)
        if now is None:
            break
        pageIndex += 1

    print(f"\tGet News' Text Data About '{COMPANY_NAME}'")

    for index in range(len(new_list)):
        response = requests.get(new_list[index]["URL"], headers=HEADERS)
        html = bs(response.text, 'html.parser')
        news_text = bs(str(html.select_one('#news_read')).split('<div class="link_news">')[0].split('\t')[-1], 'html.parser').get_text().strip()
        collected_text += len(news_text)
        new_list[index]["내용"] = news_text
    
    print(f"\tCollected News : {len(new_list)}")
    print(f"\tCollected Text : {collected_text - prevText}")
    
    prevText = collected_text

    news_list += new_list
    pickle.dump((idx, news_list, collected_text), open(DATA_PATH+"saved_news.pkl", "wb"))

print("Saving...")

news_df = pd.DataFrame(news_list)

news_df.to_csv(DATA_PATH+"News_Info.csv", index=False, encoding='utf-8')

print("Complete")
