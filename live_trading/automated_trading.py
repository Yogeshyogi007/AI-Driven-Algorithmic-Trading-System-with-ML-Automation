import schedule
import time
import logging
import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from utils.config import NIFTY_50_STOCKS, RSI_BUY_THRESHOLD, SMA_SHORT, SMA_LONG
from utils.google_sheets import GoogleSheetsLogger
from strategies.assignment_strategy import AssignmentTradingStrategy
# Telegram alert function
def send_telegram_alert(message):
    """Send Telegram alert (placeholder - configure in config.py)"""
    try:
        from utils.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        import requests
        
        if TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN":
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
            requests.get(url)
            print(f"📱 Telegram alert sent: {message[:50]}...")
        else:
            print(f"📱 Telegram alert (not configured): {message[:50]}...")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedTradingSystem:
    """
    Automated Trading System for Assignment Requirements
    - Scans NIFTY 50 stocks
    - Runs assignment strategy
    - Logs to Google Sheets
    - Sends Telegram alerts
    """
    
    def __init__(self, google_sheets_enabled=True, telegram_enabled=True):
        """
        Initialize the automated trading system
        
        Args:
            google_sheets_enabled (bool): Enable Google Sheets logging
            telegram_enabled (bool): Enable Telegram alerts
        """
        self.google_sheets_enabled = google_sheets_enabled
        self.telegram_enabled = telegram_enabled
        
        # Initialize components
        self.strategy = AssignmentTradingStrategy(
            rsi_buy_threshold=RSI_BUY_THRESHOLD,
            sma_short=SMA_SHORT,
            sma_long=SMA_LONG
        )
        
        # Initialize Google Sheets logger
        if self.google_sheets_enabled:
            try:
                from utils.config import GOOGLE_SHEETS_CREDENTIALS_FILE, SPREADSHEET_ID
                self.sheets_logger = GoogleSheetsLogger(
                    GOOGLE_SHEETS_CREDENTIALS_FILE, 
                    SPREADSHEET_ID
                )
                logger.info("✅ Google Sheets integration initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Sheets: {e}")
                self.google_sheets_enabled = False
        
        # Track performance metrics
        self.total_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        logger.info("🚀 Automated Trading System initialized")
    
    def scan_market(self):
        """
        Scan the market for trading opportunities
        """
        logger.info("🔍 Starting market scan...")
        
        try:
            # Select top 3 NIFTY 50 stocks for demonstration
            selected_symbols = NIFTY_50_STOCKS[:3]
            logger.info(f"📊 Scanning {len(selected_symbols)} symbols: {selected_symbols}")
            
            # Run strategy analysis
            results = self.strategy.run_strategy_for_symbols(selected_symbols, period="6mo")
            
            # Process results and generate signals
            signals = self.process_results(results)
            
            # Log results to Google Sheets
            if self.google_sheets_enabled:
                self.log_results_to_sheets(results, signals)
            
            # Send alerts
            if self.telegram_enabled:
                self.send_alerts(signals)
            
            logger.info("✅ Market scan completed")
            
        except Exception as e:
            logger.error(f"❌ Error during market scan: {e}")
            if self.telegram_enabled:
                send_telegram_alert(f"❌ Market scan error: {e}")
    
    def process_results(self, results):
        """
        Process strategy results and generate current signals
        
        Args:
            results (dict): Strategy results for all symbols
            
        Returns:
            list: List of current trading signals
        """
        signals = []
        
        for symbol, result in results.items():
            df = result['data']
            backtest = result['backtest']
            
            # Get latest data point
            latest = df.iloc[-1]
            
            # Check for current signals
            current_signal = latest['Signal']
            current_price = latest['Close']
            current_rsi = latest['RSI']
            current_sma_20 = latest['SMA_20']
            current_sma_50 = latest['SMA_50']
            
            # Calculate confidence based on signal strength
            confidence = latest['Signal_Strength']
            
            if current_signal != 'HOLD':
                signal_info = {
                    'symbol': symbol,
                    'signal': current_signal,
                    'price': current_price,
                    'confidence': confidence,
                    'indicators': {
                        'RSI': current_rsi,
                        'SMA_20': current_sma_20,
                        'SMA_50': current_sma_50,
                        'MACD': latest['MACD']
                    },
                    'backtest_performance': {
                        'total_return': backtest['total_return'],
                        'win_rate': backtest['win_rate'],
                        'total_pnl': backtest['total_pnl']
                    }
                }
                signals.append(signal_info)
                
                logger.info(f"📈 Signal for {symbol}: {current_signal} at ${current_price:.2f}")
        
        return signals
    
    def log_results_to_sheets(self, results, signals):
        """
        Log results to Google Sheets
        
        Args:
            results (dict): Strategy results
            signals (list): Current signals
        """
        try:
            # Log signals
            for signal in signals:
                self.sheets_logger.log_signal(
                    signal['symbol'],
                    signal['signal'],
                    signal['price'],
                    signal['confidence'],
                    signal['indicators']
                )
            
            # Calculate overall performance
            total_pnl = sum([r['backtest']['total_pnl'] for r in results.values()])
            total_trades = sum([r['backtest']['total_trades'] for r in results.values()])
            winning_trades = sum([r['backtest']['winning_trades'] for r in results.values()])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Update P&L summary
            self.sheets_logger.update_pnl_summary(
                total_pnl, winning_trades, total_trades, win_rate
            )
            
            logger.info(f"✅ Results logged to Google Sheets - Total P&L: ${total_pnl:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error logging to Google Sheets: {e}")
    
    def send_alerts(self, signals):
        """
        Send Telegram alerts for signals
        
        Args:
            signals (list): List of trading signals
        """
        if not signals:
            return
        
        for signal in signals:
            message = f"""
📊 Trading Signal Alert

Symbol: {signal['symbol']}
Signal: {signal['signal']}
Price: ${signal['price']:.2f}
Confidence: {signal['confidence']:.2f}

Technical Indicators:
• RSI: {signal['indicators']['RSI']:.2f}
• SMA 20: ${signal['indicators']['SMA_20']:.2f}
• SMA 50: ${signal['indicators']['SMA_50']:.2f}
• MACD: {signal['indicators']['MACD']:.4f}

Backtest Performance:
• Total Return: {signal['backtest_performance']['total_return']:.2f}%
• Win Rate: {signal['backtest_performance']['win_rate']:.2f}%
• Total P&L: ${signal['backtest_performance']['total_pnl']:.2f}
            """
            
            try:
                send_telegram_alert(message)
                logger.info(f"✅ Alert sent for {signal['symbol']}")
            except Exception as e:
                logger.error(f"❌ Failed to send alert: {e}")
    
    def run_scheduled_scan(self):
        """
        Run scheduled market scan
        """
        logger.info("⏰ Running scheduled market scan...")
        self.scan_market()
    
    def start_automation(self, scan_interval_minutes=30):
        """
        Start the automated trading system
        
        Args:
            scan_interval_minutes (int): Minutes between market scans
        """
        logger.info(f"🚀 Starting automated trading system (scan every {scan_interval_minutes} minutes)")
        
        # Schedule market scans
        schedule.every(scan_interval_minutes).minutes.do(self.run_scheduled_scan)
        
        # Run initial scan
        self.run_scheduled_scan()
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Automated trading system stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in automation loop: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """
    Main function to run the automated trading system
    """
    print("🤖 AI-Driven Algorithmic Trading System")
    print("=" * 50)
    
    # Initialize system
    trading_system = AutomatedTradingSystem(
        google_sheets_enabled=True,
        telegram_enabled=True
    )
    
    # Start automation
    try:
        trading_system.start_automation(scan_interval_minutes=30)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
