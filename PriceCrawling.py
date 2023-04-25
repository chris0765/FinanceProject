from bs4 import BeautifulSoup as bs
import datetime
import pandas as pd
import requests
import time
import os
import pickle5 as pickle

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

PRICE_URL_BASIC = 'https://finance.naver.com/item/sise_day.nhn?'
HEADERS = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

prices_df = pd.DataFrame()
prices_list = []
collected_prices = 0

try:
    saved_index, prices_list, collected_prices = pickle.load(open(DATA_PATH+"saved_prices.pkl", "rb"))
except:
    saved_index, prices_list, collected_prices = (-1, [], 0)

for idx, row in COMPANY_CODES.iterrows():
    if idx <= saved_index:
        continue
    COMPANY_CODE = row["단축코드"]
    COMPANY_NAME = row["한글 종목약명"]
    print(f"Price about '{COMPANY_NAME}' is now crawling({idx+1}/{len(COMPANY_CODES)})...{(idx+1)*100//len(COMPANY_CODES)}%")
    print(f"\tGet Price About '{COMPANY_NAME}'")

    pageIndex = 1
    now = datetime.datetime.strptime(time.strftime("%Y.%m.%d", time.localtime(time.time())), "%Y.%m.%d")
    while True:
        priceUrl = PRICE_URL_BASIC + f"code={row['단축코드']}&page={pageIndex}"
        now = datetime.datetime.strptime(time.strftime("%Y.%m.%d", time.localtime(time.time())), "%Y.%m.%d")
        response = requests.get(priceUrl, headers=HEADERS)

        html = bs(response.text, 'html.parser')
        navis = html.select("body > table.Nnavi > tr > td")
        
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

        trs = html.select("body > table.type2 > tr")

        for tr in trs:
            tds = None
            try:
                tds = tr.select("td")
                if len(tds) != 7:
                    continue
            except:
                continue
            if tds[0].get_text().strip() == '':
                now = None
                break
            prices_dict = {"한글 종목약명": COMPANY_NAME, "단축코드": COMPANY_CODE}
            prices_dict["날짜"] = tds[0].get_text().strip()
            prices_dict["종가"] = "".join(tds[1].get_text().strip().split(","))
            try:
                if tds[2].select_one('img')['alt'] == "하락":
                    prices_dict["상승/하락"] = -1
                else:
                    prices_dict["상승/하락"] = 1
            except:
                prices_dict["상승/하락"] = 0
            prices_dict["전일비"] = "".join(tds[2].get_text().strip().split(","))
            prices_dict["시가"] = "".join(tds[3].get_text().strip().split(","))
            prices_dict["고가"] = "".join(tds[4].get_text().strip().split(","))
            prices_dict["저가"] = "".join(tds[5].get_text().strip().split(","))
            prices_dict["거래량"] = "".join(tds[6].get_text().strip().split(","))
            date = datetime.datetime.strptime(prices_dict["날짜"], "%Y.%m.%d")
            if (now-date).days > 100:
                now = None
                break
            prices_list.append(prices_dict)

        if now is None:
            break

        pageIndex += 1
    
    print(f"\tCollected Price : {len(prices_list) - collected_prices}")

    collected_prices = len(prices_list)
    pickle.dump((idx, prices_list, collected_prices), open(DATA_PATH+"saved_prices.pkl", "wb"))

prices_df = pd.DataFrame(prices_list)
prices_df.to_csv(DATA_PATH+"Price_Info.csv", index=False, encoding='utf-8')
print("Complete")
