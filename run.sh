echo "Install pip libraries..."
pip install -r requirements.txt
echo "Get Company Info..."
python CompanyCodeCrawling.py
echo "Crawling finance news data..."
python NewsCrawling.py
echo "Crawling stock price data..."
python PriceCrawling.py
echo "Train&Test model..."
python main.py