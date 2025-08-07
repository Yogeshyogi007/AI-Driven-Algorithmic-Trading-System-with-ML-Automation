import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker, start_date, end_date, save_path="data/"):
    """
    Fetches historical stock market data from Yahoo Finance and saves it as a CSV file.
    """
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    
    data = yf.download(ticker, start=start_date, end=end_date)

    # Ensure correct columns & format
    data.reset_index(inplace=True)
    data = data[["Date", "Close", "High", "Low", "Open", "Volume"]]

    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)

    # Save the cleaned CSV
    file_path = os.path.join(save_path, f"{ticker}_data.csv")
    data.to_csv(file_path, index=False)
    
    print(f"✅ Data saved successfully at: {file_path}")

    return data

# Run function
if __name__ == "__main__":
    fetch_stock_data("TSLA", "2020-01-01", "2024-01-01")
