import pymc3 as pm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import requests
from bs4 import BeautifulSoup

# Exchanges with yfinance support (for equity/commodity tickers)
YFINANCE_EQUITIES = {
    "NYSE": ["AAPL", "MSFT", "GOOGL"],
    "NASDAQ": ["TSLA", "NVDA", "AMZN"],
    "LSE": ["HSBA.L", "VOD.L"],  # London Stock Exchange
    "HKEX": ["0700.HK", "1299.HK"],  # Hong Kong
    "Euronext": ["SAN.PA", "OR.PA"],  # Paris
    "SIX": ["ROG.SW", "NESN.SW"],  # Switzerland
    "TSE": ["7203.T", "9984.T"],  # Tokyo
    "BSE": ["RELIANCE.BO", "TCS.BO"],  # Bombay
    "NSE": ["RELIANCE.NS", "TCS.NS"],  # National Stock Exchange India
    "Shanghai-SE": ["600519.SS", "601318.SS"],
    "Shenzhen-SE": ["000001.SZ", "000002.SZ"],
    # Add more supported tickers as needed
}
YFINANCE_COMMODITIES = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Oil": "CL=F",
    "NaturalGas": "NG=F",
    "Copper": "HG=F",
    # Add more commodities as needed
}

# Exchanges needing webscraping (or mock if scraping fails)
SCRAPE_EXCHANGES = {
    "DSE-BD": [
        {"url": "https://www.dsebd.org/latest_share_price_scroll_l.php", "symbol": "GP"},
        {"url": "https://www.dsebd.org/latest_share_price_scroll_l.php", "symbol": "BATBC"},
    ],
    "CSE-BD": [
        {"url": "https://www.cse.com.bd/market/current_price", "symbol": "BSCCL"},
        {"url": "https://www.cse.com.bd/market/current_price", "symbol": "CITYBANK"},
    ],
    "Dubai-SE": [
        {"url": "https://www.dfm.ae/market-watch", "symbol": "EMAAR"},
        {"url": "https://www.dfm.ae/market-watch", "symbol": "DU"},
    ],
    "Karachi-SE": [
        {"url": "https://www.psx.com.pk/market-summary", "symbol": "HBL"},
        {"url": "https://www.psx.com.pk/market-summary", "symbol": "OGDC"},
    ],
    # Add more as needed, with actual scraping URLs and symbols
}
MOCK_EXCHANGES = [
    "JSE-SouthAfrica", "BMV-Mexico", "TWSE-Taiwan", "ASX-Australia", 
    "Moscow-SE", "Tadawul-Saudi", "TSX-Toronto", "Bovespa-Brazil"
    # Add more as needed
]

def fetch_yfinance_equity(ticker, period="1y"):
    try:
        data = yf.download(ticker, period=period)
        prices = data['Close']
        returns = prices.pct_change().dropna()
        return prices, returns
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        prices = pd.Series(np.random.normal(100, 10, size=100))
        returns = prices.pct_change().dropna()
        return prices, returns

def fetch_yfinance_commodity(ticker, period="1y"):
    try:
        data = yf.download(ticker, period=period)
        prices = data['Close']
        returns = prices.pct_change().dropna()
        return prices, returns
    except Exception as e:
        print(f"Error fetching commodity {ticker}: {e}")
        prices = pd.Series(np.random.normal(1800, 10, size=100))
        returns = prices.pct_change().dropna()
        return prices, returns

def fetch_webscrape(exchange, symbol, url):
    '''
    Placeholder for webscraping logic.
    For each SE, parse the page and extract the historical price series for symbol.
    If scraping fails, return mock data.
    '''
    print(f"Webscraping {exchange} {symbol} from {url} ...")
    try:
        # Example for DSE-BD (this is a placeholder, real parsing needed)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Here you'd parse the table and extract prices for the symbol.
        # For demonstration, return mock data:
        prices = pd.Series(np.cumsum(np.random.normal(0, 1, size=100)) + 100)
        returns = prices.pct_change().dropna()
        return prices, returns
    except Exception as e:
        print(f"Error scraping {exchange} {symbol}: {e}")
        prices = pd.Series(np.cumsum(np.random.normal(0, 1, size=100)) + 100)
        returns = prices.pct_change().dropna()
        return prices, returns

def fetch_mock(exchange, label="MOCK", size=100):
    # For SEs and commodities without API/scraping support: Use mock data
    np.random.seed(abs(hash(label)) % 100000)
    prices = pd.Series(np.cumsum(np.random.normal(0, 1, size=size)) + 100)
    returns = prices.pct_change().dropna()
    return prices, returns

def bayesian_stats(returns):
    with pm.Model() as model:
        mu = pm.Normal('mu', mu=0, sigma=1)
        sigma = pm.HalfNormal('sigma', sigma=1)
        obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=returns)
        trace = pm.sample(1000, progressbar=False)
    return np.mean(trace['mu']), np.std(trace['mu'])

def analyze_plot(prices, returns, label):
    mean_return = np.mean(returns)
    volatility = np.std(returns)
    bayes_mean, bayes_std = bayesian_stats(returns)
    print(f"\n{label} Analysis:")
    print(f"- Mean daily return: {mean_return:.4f}")
    print(f"- Volatility (std): {volatility:.4f}")
    print(f"- Bayesian mean return: {bayes_mean:.4f} (std: {bayes_std:.4f})")

    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    prices.plot(title=f"{label} Price")
    plt.subplot(1,2,2)
    returns.plot(title=f"{label} Daily Returns")
    plt.tight_layout()
    plt.show()

def run_analysis():
    # Equities - yfinance supported
    for ex, tickers in YFINANCE_EQUITIES.items():
        for ticker in tickers:
            prices, returns = fetch_yfinance_equity(ticker)
            analyze_plot(prices, returns, f"{ex} ({ticker})")
    # Equities - webscraping exchanges
    for ex, stocks in SCRAPE_EXCHANGES.items():
        for stock in stocks:
            prices, returns = fetch_webscrape(ex, stock['symbol'], stock['url'])
            analyze_plot(prices, returns, f"{ex} ({stock['symbol']})")
    # Equities - mock exchanges
    for ex in MOCK_EXCHANGES:
        for i in range(2):  # Two sample stocks per exchange
            label = f"{ex}-Stock-{i+1}"
            prices, returns = fetch_mock(ex, label)
            analyze_plot(prices, returns, label)
    # Commodities - yfinance supported
    for c_name, c_ticker in YFINANCE_COMMODITIES.items():
        prices, returns = fetch_yfinance_commodity(c_ticker)
        analyze_plot(prices, returns, f"Commodity ({c_name})")
    # Commodities - mock exchanges
    for i in range(2):  # Two sample commodities
        label = f"Mock-Commodity-{i+1}"
        prices, returns = fetch_mock("Mock-Commodity", label)
        analyze_plot(prices, returns, label)

if __name__ == "__main__":
    run_analysis()
