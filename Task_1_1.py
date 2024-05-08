from sec_edgar_downloader import Downloader
import os

def download_10k_filings(ticker):
    # Initialize the downloader
    dl = Downloader()

    # Create a directory to store the filings
    directory = f'{ticker}_10k_filings'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Loop through each year from 1995 to 2023
    for year in range(1995, 2024):
        try:
            # Download the 10-K filing for the current year
            dl.get("10-K", ticker, year)
            print(f"Downloaded {ticker} 10-K filing for {year}")
        except Exception as e:
            print(f"Failed to download {ticker} 10-K filing for {year}: {e}")

# Usage for three company tickers
tickers = ['AAPL', 'NVDA', 'TSLA']

for ticker in tickers:
    download_10k_filings(ticker)