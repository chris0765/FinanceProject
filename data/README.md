# FinanceProject/data

프로그램이 동작하며 크롤링한 데이터가 저장되는 디렉토리입니다.
* data_* : 각 종목의 단축코드를 수집한 데이터입니다. 종목명, 종목코드, 단축코드, 종목 약명 등의 정보가 존재합니다.
* News_Info.csv : 각 종목의 최근 100일간 관련 뉴스를 수집한 데이터입니다. 뉴스명, URL, 뉴스 내용 등의 데이터가 존재합니다.
* Price_Info.csv : 각 종목의 최근 100일간 가격 데이터입니다. 전일대비 증가, 종가, 시가, 고가, 저가, 거래량 등의 정보가 존재합니다.
* saved_news.pkl : 뉴스 데이터를 수집하는 중 중단에 대비하기 위한 백업파일입니다. 뉴스 데이터 수집 중 수집이 중단된 이후 다시 프로그램을 실행하면 중단 이전 시점에 이어서 데이터를 받습니다.

모든 파일은 run.sh를 새로 실행할 때마다 새롭게 갱신됩니다.