import pandas as pd
import numpy as np
import yfinance as yf
import ta
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssignmentTradingStrategy:
    """
    Trading Strategy for Assignment Requirements:
    - RSI < 30 as buy signal
    - Confirm with 20-DMA crossing above 50-DMA
    - Backtest for 6 months
    """
    
    def __init__(self, rsi_buy_threshold=30, rsi_sell_threshold=70, 
                 sma_short=20, sma_long=50):
        """
        Initialize strategy parameters
        
        Args:
            rsi_buy_threshold (int): RSI threshold for buy signal
            rsi_sell_threshold (int): RSI threshold for sell signal
            sma_short (int): Short-term SMA period
            sma_long (int): Long-term SMA period
        """
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.sma_short = sma_short
        self.sma_long = sma_long
        
    def fetch_nifty_data(self, symbols, period="6mo"):
        """
        Fetch data for NIFTY 50 stocks
        
        Args:
            symbols (list): List of stock symbols
            period (str): Data period (6mo for 6 months)
            
        Returns:
            dict: Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        
        for symbol in symbols:
            try:
                logger.info(f"📊 Fetching data for {symbol}...")
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                
                if not df.empty:
                    # Calculate technical indicators
                    df = self.calculate_indicators(df)
                    data[symbol] = df
                    logger.info(f"✅ Data fetched for {symbol}: {len(df)} days")
                else:
                    logger.warning(f"⚠️ No data available for {symbol}")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching data for {symbol}: {e}")
                
        return data
    
    def calculate_indicators(self, df):
        """
        Calculate technical indicators for the strategy
        
        Args:
            df (DataFrame): Stock price data
            
        Returns:
            DataFrame: Data with indicators added
        """
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # Moving Averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=self.sma_short)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=self.sma_long)
        
        # MACD
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        
        # Volume indicators
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        return df
    
    def generate_signals(self, df):
        """
        Generate buy/sell signals based on assignment strategy
        
        Args:
            df (DataFrame): Data with indicators
            
        Returns:
            DataFrame: Data with signals added
        """
        df = df.copy()
        
        # Initialize signal columns
        df['Signal'] = 'HOLD'
        df['Signal_Strength'] = 0.0
        
        for i in range(1, len(df)):
            current_rsi = df['RSI'].iloc[i]
            current_sma_20 = df['SMA_20'].iloc[i]
            current_sma_50 = df['SMA_50'].iloc[i]
            prev_sma_20 = df['SMA_20'].iloc[i-1]
            prev_sma_50 = df['SMA_50'].iloc[i-1]
            
            # Buy Signal: RSI < 30 AND 20-DMA crosses above 50-DMA
            if (current_rsi < self.rsi_buy_threshold and 
                prev_sma_20 <= prev_sma_50 and 
                current_sma_20 > current_sma_50):
                
                df.loc[df.index[i], 'Signal'] = 'BUY'
                df.loc[df.index[i], 'Signal_Strength'] = (self.rsi_buy_threshold - current_rsi) / self.rsi_buy_threshold
            
            # Sell Signal: RSI > 70 OR 20-DMA crosses below 50-DMA
            elif (current_rsi > self.rsi_sell_threshold or 
                  (prev_sma_20 >= prev_sma_50 and current_sma_20 < current_sma_50)):
                
                df.loc[df.index[i], 'Signal'] = 'SELL'
                df.loc[df.index[i], 'Signal_Strength'] = (current_rsi - self.rsi_sell_threshold) / (100 - self.rsi_sell_threshold)
        
        return df
    
    def backtest_strategy(self, df, initial_capital=10000):
        """
        Backtest the trading strategy
        
        Args:
            df (DataFrame): Data with signals
            initial_capital (float): Initial capital for backtesting
            
        Returns:
            dict: Backtest results
        """
        df = df.copy()
        
        # Initialize backtest variables
        capital = initial_capital
        shares = 0
        trades = []
        buy_price = 0
        
        # Track portfolio value
        df['Portfolio_Value'] = capital
        df['Shares_Held'] = 0
        
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            signal = df['Signal'].iloc[i]
            
            # Execute trades
            if signal == 'BUY' and shares == 0:
                # Buy signal
                shares = capital / current_price
                buy_price = current_price
                capital = 0
                
                trades.append({
                    'Date': df.index[i],
                    'Action': 'BUY',
                    'Price': current_price,
                    'Shares': shares,
                    'Value': shares * current_price
                })
                
            elif signal == 'SELL' and shares > 0:
                # Sell signal
                sell_value = shares * current_price
                capital = sell_value
                
                trades.append({
                    'Date': df.index[i],
                    'Action': 'SELL',
                    'Price': current_price,
                    'Shares': shares,
                    'Value': sell_value,
                    'P&L': sell_value - (shares * buy_price)
                })
                
                shares = 0
                buy_price = 0
            
            # Update portfolio value
            current_value = capital + (shares * current_price)
            df.loc[df.index[i], 'Portfolio_Value'] = current_value
            df.loc[df.index[i], 'Shares_Held'] = shares
        
        # Calculate performance metrics
        final_value = df['Portfolio_Value'].iloc[-1]
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        # Calculate win rate
        winning_trades = [t for t in trades if t.get('P&L', 0) > 0]
        win_rate = (len(winning_trades) / len([t for t in trades if 'P&L' in t])) * 100 if len([t for t in trades if 'P&L' in t]) > 0 else 0
        
        # Calculate total P&L
        total_pnl = sum([t.get('P&L', 0) for t in trades])
        
        results = {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'total_trades': len([t for t in trades if 'P&L' in t]),
            'winning_trades': len(winning_trades),
            'trades': trades,
            'portfolio_data': df
        }
        
        return results
    
    def run_strategy_for_symbols(self, symbols, period="6mo"):
        """
        Run the complete strategy for multiple symbols
        
        Args:
            symbols (list): List of stock symbols
            period (str): Data period
            
        Returns:
            dict: Results for all symbols
        """
        logger.info(f"🚀 Starting strategy analysis for {len(symbols)} symbols...")
        
        # Fetch data for all symbols
        data = self.fetch_nifty_data(symbols, period)
        
        results = {}
        
        for symbol, df in data.items():
            logger.info(f"📈 Analyzing {symbol}...")
            
            # Generate signals
            df_with_signals = self.generate_signals(df)
            
            # Backtest strategy
            backtest_results = self.backtest_strategy(df_with_signals)
            
            results[symbol] = {
                'data': df_with_signals,
                'backtest': backtest_results
            }
            
            logger.info(f"✅ {symbol} analysis complete - Return: {backtest_results['total_return']:.2f}%, Win Rate: {backtest_results['win_rate']:.2f}%")
        
        return results
