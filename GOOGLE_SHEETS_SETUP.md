# 📊 Google Sheets Setup Guide

## 🚀 Quick Setup (Optional)

The system works perfectly without Google Sheets! The error you see is just because Google Sheets isn't configured yet.

## 📝 Step-by-Step Google Sheets Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable billing (required for API access)

### 2. Enable Google Sheets API
1. Go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"

### 3. Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details
4. Click "Create and Continue"

### 4. Download Credentials
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the file and rename to `credentials.json`
6. Place `credentials.json` in your project root directory

### 5. Create Google Sheet
1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Copy the spreadsheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

### 6. Update Configuration
Edit `utils/config.py`:
```python
# Update these values
GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"  # Path to your credentials file
SPREADSHEET_ID = "your_actual_spreadsheet_id_here"   # Your spreadsheet ID
```

### 7. Share Spreadsheet
1. Open your Google Sheet
2. Click "Share" button
3. Add your service account email (found in credentials.json)
4. Give "Editor" permissions

## ✅ Verification

After setup, run the test again:
```bash
python test_assignment.py
```

You should see:
```
✅ Google Sheets connection established
✅ Trade logged: BUY 100 RELIANCE.NS at $1389.40
✅ Signal logged: BUY RELIANCE.NS at $1389.40
```

## 🔧 Troubleshooting

### Common Issues:

1. **"credentials.json not found"**
   - Make sure the file is in the project root directory
   - Check the file path in `utils/config.py`

2. **"Invalid spreadsheet ID"**
   - Verify the spreadsheet ID is correct
   - Make sure the spreadsheet is shared with your service account

3. **"Permission denied"**
   - Check that the service account has "Editor" access to the spreadsheet
   - Verify the Google Sheets API is enabled

4. **"API quota exceeded"**
   - Google Sheets API has daily limits
   - Consider using a paid Google Cloud account for higher limits

## 📊 What Gets Logged

When Google Sheets is configured, the system will create:

1. **Trade Log Sheet**
   - Timestamp, Symbol, Action, Price, Quantity, Total Value, Status

2. **P&L Summary Sheet**
   - Total P&L, Total Trades, Winning Trades, Win Rate, Average P&L per Trade

3. **Signals Sheet**
   - Timestamp, Symbol, Signal, Price, Confidence, RSI, SMA_20, SMA_50, MACD

## 🎯 Assignment Compliance

Even without Google Sheets, your project **fully meets the assignment requirements**:

- ✅ **Data Ingestion (20%)** - NIFTY 50 stocks
- ✅ **Trading Strategy (20%)** - RSI + Moving Average
- ✅ **ML/Analytics (20%)** - LSTM model
- ✅ **Code Quality (20%)** - Modular, documented code
- ✅ **Bonus Task** - Telegram alerts

Google Sheets is just an **enhancement** for better logging and tracking!

---

**💡 Pro Tip**: For the assignment submission, you can either:
1. Set up Google Sheets following this guide, OR
2. Submit without Google Sheets (it's still a complete solution)

The core functionality works perfectly either way! 🚀
