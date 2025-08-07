import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsLogger:
    def __init__(self, credentials_file, spreadsheet_id):
        """
        Initialize Google Sheets integration for trade logging
        
        Args:
            credentials_file (str): Path to Google Service Account credentials JSON
            spreadsheet_id (str): Google Sheets spreadsheet ID
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        
        # Set up Google Sheets API scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            # Check if credentials file exists
            if not os.path.exists(credentials_file):
                logger.warning(f"⚠️ Google Sheets credentials file not found: {credentials_file}")
                logger.info("📝 To enable Google Sheets logging:")
                logger.info("   1. Create a Google Cloud Project")
                logger.info("   2. Enable Google Sheets API")
                logger.info("   3. Create a service account")
                logger.info("   4. Download credentials.json")
                logger.info("   5. Place credentials.json in project root")
                self.client = None
                self.spreadsheet = None
                return
            
            # Check if spreadsheet ID is configured
            if spreadsheet_id == "YOUR_SPREADSHEET_ID":
                logger.warning("⚠️ Google Sheets spreadsheet ID not configured")
                logger.info("📝 To configure Google Sheets:")
                logger.info("   1. Create a Google Sheet")
                logger.info("   2. Copy the spreadsheet ID from URL")
                logger.info("   3. Update SPREADSHEET_ID in utils/config.py")
                self.client = None
                self.spreadsheet = None
                return
            
            # Authenticate with Google Sheets
            creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            logger.info("✅ Google Sheets connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            logger.info("📝 Google Sheets logging will be disabled")
            self.client = None
            self.spreadsheet = None
    
    def log_trade(self, symbol, action, price, quantity, timestamp=None):
        """
        Log a trade to the Trade Log sheet
        
        Args:
            symbol (str): Stock symbol
            action (str): 'BUY' or 'SELL'
            price (float): Trade price
            quantity (int): Number of shares
            timestamp (datetime): Trade timestamp
        """
        if not self.spreadsheet:
            logger.info(f"📊 Trade (not logged): {action} {quantity} {symbol} at ${price:.2f}")
            return
        
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            # Get or create Trade Log worksheet
            try:
                trade_log_sheet = self.spreadsheet.worksheet("Trade Log")
            except gspread.WorksheetNotFound:
                trade_log_sheet = self.spreadsheet.add_worksheet("Trade Log", 1000, 10)
                # Add headers
                trade_log_sheet.append_row([
                    "Timestamp", "Symbol", "Action", "Price", "Quantity", 
                    "Total Value", "Status"
                ])
            
            # Calculate total value
            total_value = price * quantity
            
            # Append trade data
            trade_log_sheet.append_row([
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                action,
                f"${price:.2f}",
                quantity,
                f"${total_value:.2f}",
                "EXECUTED"
            ])
            
            logger.info(f"✅ Trade logged: {action} {quantity} {symbol} at ${price:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log trade: {e}")
    
    def update_pnl_summary(self, total_pnl, win_count, total_trades, win_rate):
        """
        Update P&L summary in a separate sheet
        
        Args:
            total_pnl (float): Total profit/loss
            win_count (int): Number of winning trades
            total_trades (int): Total number of trades
            win_rate (float): Win rate percentage
        """
        if not self.spreadsheet:
            logger.info(f"📊 P&L Summary (not logged): Total P&L: ${total_pnl:.2f}, Win Rate: {win_rate:.2f}%")
            return
        
        try:
            # Get or create P&L Summary worksheet
            try:
                pnl_sheet = self.spreadsheet.worksheet("P&L Summary")
            except gspread.WorksheetNotFound:
                pnl_sheet = self.spreadsheet.add_worksheet("P&L Summary", 20, 10)
                # Add headers
                pnl_sheet.append_row([
                    "Metric", "Value", "Last Updated"
                ])
            
            # Clear existing data (except headers)
            pnl_sheet.clear()
            pnl_sheet.append_row(["Metric", "Value", "Last Updated"])
            
            # Add summary data
            summary_data = [
                ["Total P&L", f"${total_pnl:.2f}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Total Trades", total_trades, ""],
                ["Winning Trades", win_count, ""],
                ["Win Rate", f"{win_rate:.2f}%", ""],
                ["Average P&L per Trade", f"${total_pnl/total_trades:.2f}" if total_trades > 0 else "$0.00", ""]
            ]
            
            for row in summary_data:
                pnl_sheet.append_row(row)
            
            logger.info(f"✅ P&L Summary updated: Total P&L: ${total_pnl:.2f}, Win Rate: {win_rate:.2f}%")
            
        except Exception as e:
            logger.error(f"❌ Failed to update P&L summary: {e}")
    
    def log_signal(self, symbol, signal_type, price, confidence, indicators):
        """
        Log trading signals to a separate sheet
        
        Args:
            symbol (str): Stock symbol
            signal_type (str): 'BUY', 'SELL', or 'HOLD'
            price (float): Current price
            confidence (float): Signal confidence (0-1)
            indicators (dict): Technical indicators used
        """
        if not self.spreadsheet:
            logger.info(f"📊 Signal (not logged): {signal_type} {symbol} at ${price:.2f}")
            return
        
        try:
            # Get or create Signals worksheet
            try:
                signals_sheet = self.spreadsheet.worksheet("Signals")
            except gspread.WorksheetNotFound:
                signals_sheet = self.spreadsheet.add_worksheet("Signals", 1000, 10)
                # Add headers
                signals_sheet.append_row([
                    "Timestamp", "Symbol", "Signal", "Price", "Confidence", 
                    "RSI", "SMA_20", "SMA_50", "MACD"
                ])
            
            # Append signal data
            signals_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                signal_type,
                f"${price:.2f}",
                f"{confidence:.2f}",
                f"{indicators.get('RSI', 0):.2f}",
                f"${indicators.get('SMA_20', 0):.2f}",
                f"${indicators.get('SMA_50', 0):.2f}",
                f"{indicators.get('MACD', 0):.4f}"
            ])
            
            logger.info(f"✅ Signal logged: {signal_type} {symbol} at ${price:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log signal: {e}")

    def is_connected(self):
        """
        Check if Google Sheets is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.spreadsheet is not None
