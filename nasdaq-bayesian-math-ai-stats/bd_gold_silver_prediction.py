import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import yfinance as yf

INTERNATIONAL_GOLD_TICKER = "GC=F"  # Gold Futures (USD/oz)
INTERNATIONAL_SILVER_TICKER = "SI=F"  # Silver Futures (USD/oz)

def scrape_bd_gold():
    # Example: Scrape from Bangladesh Jewellers Samity (BAJUS)
    # Actual URLs may change, update if needed
    url = "https://bajus.org/price/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        table = soup.find("table")
        gold_price = None
        silver_price = None
        for row in table.find_all("tr")[1:]:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if "22 carat" in cols[0].lower():
                gold_price = float(cols[1].replace(',', ''))  # per gram BDT
            if "silver" in cols[0].lower():
                silver_price = float(cols[1].replace(',', ''))
        return gold_price, silver_price
    except Exception as e:
        print("Error scraping BD market prices:", e)
        return None, None

def get_international_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, interval="1mo")["Close"].dropna()
    df.index = df.index.strftime("%Y-%m-%d")
    return df

def simulate_bd_history(scraper_func, months=36):
    # Simulate BD market history by scraping latest and projecting backwards
    gold, silver = scraper_func()
    today = datetime.today()
    dates = [today - timedelta(days=30*i) for i in range(months)][::-1]
    # Simulate steady annual increase (historical pattern)
    golds = [gold * (1 - 0.08 + 0.16 * i/months) for i in range(months)]
    silvers = [silver * (1 - 0.07 + 0.14 * i/months) for i in range(months)]
    df = pd.DataFrame({
        "date": dates,
        "gold_price": golds,
        "silver_price": silvers
    })
    df.set_index("date", inplace=True)
    return df

def forecast_next_3_years(df, col):
    df = df.asfreq("MS")
    x = np.arange(len(df))
    y = df[col].values
    coef = np.polyfit(x, y, 1)  # Linear regression
    poly = np.poly1d(coef)
    future_x = np.arange(len(df), len(df)+36)
    future_dates = [df.index[-1] + timedelta(days=30*(i+1)) for i in range(36)]
    future_y = poly(future_x)
    forecast_df = pd.DataFrame({col: future_y}, index=pd.to_datetime(future_dates))
    return pd.concat([df, forecast_df])

def plot_prices(bd_df, intl_df, col, title, bd_label, intl_label):
    plt.figure(figsize=(10,5))
    plt.plot(bd_df.index, bd_df[col], 'o-', label=bd_label)
    plt.plot(intl_df.index, intl_df.values, 's-', label=intl_label)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

def analyze_investment(df, col, asset_name):
    returns = df[col].pct_change().dropna()
    avg_return = returns.mean() * 100
    volatility = returns.std() * 100
    print(f"Estimated monthly return for {asset_name}: {avg_return:.2f}%")
    print(f"Estimated monthly volatility for {asset_name}: {volatility:.2f}%")
    risk = "High" if volatility > 10 else "Medium" if volatility > 5 else "Low"
    print(f"Investment Risk Level: {risk}")
    if avg_return > 0.4:
        print(f"Potential benefit: Good growth expected for {asset_name} in BD market.")
    elif avg_return > 0.1:
        print(f"Potential benefit: Stable, modest growth for {asset_name}.")
    else:
        print(f"Potential benefit: Risk of stagnation or decline.")

def main():
    # Scrape latest BD market price
    bd_gold, bd_silver = scrape_bd_gold()
    if bd_gold is None or bd_silver is None:
        print("Failed to get BD Gold/Silver price from web.")
        return

    # Simulate BD history for last 3 years
    bd_df = simulate_bd_history(scrape_bd_gold, months=36)

    # Get international market data
    start_date = (datetime.today() - timedelta(days=36*30)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    intl_gold = get_international_data(INTERNATIONAL_GOLD_TICKER, start_date, end_date)
    intl_silver = get_international_data(INTERNATIONAL_SILVER_TICKER, start_date, end_date)

    # Forecast next 3 years for BD market
    bd_gold_forecast = forecast_next_3_years(bd_df, "gold_price")
    bd_silver_forecast = forecast_next_3_years(bd_df, "silver_price")

    # Plot comparisons
    plot_prices(bd_gold_forecast, intl_gold, "gold_price", "Gold Price: BD vs International", "BD Gold (per gram, BDT)", "Int'l Gold (per oz, USD)")
    plot_prices(bd_silver_forecast, intl_silver, "silver_price", "Silver Price: BD vs International", "BD Silver (per gram, BDT)", "Int'l Silver (per oz, USD)")

    # Investment analysis
    print("\n--- Investment Analysis: Gold ---")
    analyze_investment(bd_gold_forecast, "gold_price", "Gold")
    print("\n--- Investment Analysis: Silver ---")
    analyze_investment(bd_silver_forecast, "silver_price", "Silver")

    print("\nData is based on simulated BD market history and scraped current prices.")
    print("For more accuracy, update the scraping method for alternative BD market sources.")

if __name__ == "__main__":
    main()
