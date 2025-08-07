import pandas as pd
import ta  # Technical Analysis Library

def calculate_technical_indicators(df):
    """
    Adds technical indicators (SMA, RSI, MACD) to the stock data.

    Parameters:
    - df (DataFrame): DataFrame containing stock market data with 'Close' price.

    Returns:
    - DataFrame: Updated DataFrame with new indicator columns.
    """

    # Ensure data is sorted by date
    df = df.sort_index()

    # Simple Moving Averages (SMA)
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)  # 50-day SMA
    df["SMA_200"] = ta.trend.sma_indicator(df["Close"], window=200)  # 200-day SMA

    # Relative Strength Index (RSI)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    # Moving Average Convergence Divergence (MACD)
    df["MACD"] = ta.trend.macd(df["Close"])
    df["MACD_Signal"] = ta.trend.macd_signal(df["Close"])

    # Bollinger Bands
    df["BB_High"] = ta.volatility.bollinger_hband(df["Close"], window=20)
    df["BB_Low"] = ta.volatility.bollinger_lband(df["Close"], window=20)

    # Drop any NaN values that result from indicator calculations
    df.dropna(inplace=True)

    print("✅ Technical indicators added successfully!")
    return df

# Example Usage
if __name__ == "__main__":
    # ✅ Load the CSV once (fixed issue)
    df = pd.read_csv("data/TSLA_data.csv", skiprows=2)

    # ✅ Rename columns properly
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]

    # ✅ Convert 'Date' to datetime format and set as index
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # ✅ Calculate indicators
    df = calculate_technical_indicators(df)

    # ✅ Save the updated dataset
    df.to_csv("data/TSLA_data_with_indicators.csv")
    print("✅ Data saved with indicators at: data/TSLA_data_with_indicators.csv")

    # ✅ Display first few rows for verification
    print(df.head())
