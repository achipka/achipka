import yfinance as yf
from datetime import datetime, timedelta
import feedparser

rss_feed='http://www.nasdaqtrader.com/rss.aspx?feed=tradehalts'
feed = feedparser.parse(rss_feed)

print(feed['entries'][0]['title'])
tickerSymbol = feed['entries'][0]['title']

stock = yf.Ticker(tickerSymbol)
shares = stock.info.get('sharesOutstanding')

print(shares)



# get data on this ticker
tickerData = yf.Ticker(tickerSymbol)

# set today's date and initialize previous trading day to None
today = datetime.today()
previous_trading_day = None

# loop until previous trading day is found
while previous_trading_day is None:
    # subtract one day from today's date
    today = today - timedelta(days=1)

    # check if the resulting date is a trading day
    if tickerData.history(start=today, end=today, prepost=True).empty == False:
        previous_trading_day = today.strftime('%Y-%m-%d')

# retrieve data for the previous trading day and today
history = tickerData.history(start=previous_trading_day, end=datetime.today().strftime('%Y-%m-%d'), prepost=True)

# retrieve the previous closing price and today's high price
previous_close = history.iloc[0]['Close']
today_high = history['High'].max()

# compare the two prices and print the greater value
if previous_close > today_high:
    print("Previous closing price was greater:", previous_close)
else:
    print("Today's high price is greater:", today_high)
