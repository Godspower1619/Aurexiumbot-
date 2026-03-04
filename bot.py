# TELEGRAM XAUUSD SIGNAL BOT - SAFE 5 SIGNALS DAILY

import time
import datetime
import pandas as pd
import yfinance as yf
from telegram import Bot

# ----------------------
# CONFIGURATION
# ----------------------
BOT_TOKEN = "YOUR_NEW_TOKEN_HERE"      # <--- Replace with your BotFather token
CHAT_ID = 8480796433                    # <--- Your private chat ID
SYMBOL = "XAUUSD=X"                     # Yahoo Finance symbol for gold
TIMEFRAME = "5m"                        # 5-minute timeframe
MAX_SIGNALS = 5
signals_sent_today = 0

# EMA & RSI parameters
EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14

bot = Bot(token=BOT_TOKEN)

# ----------------------
# FUNCTIONS
# ----------------------
def get_data():
    df = yf.download(tickers=SYMBOL, period="2d", interval=TIMEFRAME)
    df['EMA_FAST'] = df['Close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['EMA_SLOW'] = df['Close'].ewm(span=EMA_SLOW, adjust=False).mean()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1*delta.clip(upper=0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def send_signal(signal_type, entry, sl, tp):
    global signals_sent_today
    if signals_sent_today >= MAX_SIGNALS:
        return
    message = f"""
{signal_type} XAUUSD

Entry: {entry:.2f}
Stop Loss: {sl:.2f}
Take Profit: {tp:.2f}

Risk:Reward 1:2
Timeframe: M5
Mode: SAFE
Confidence: High
"""
    bot.send_message(chat_id=CHAT_ID, text=message)
    signals_sent_today += 1

# ----------------------
# COMMAND RESPONSES
# ----------------------
from telegram.ext import Updater, CommandHandler

def start(update, context):
    context.bot.send_message(chat_id=CHAT_ID, text="🔥 AurexiumBot is online and ready for XAUUSD signals!")

def status(update, context):
    context.bot.send_message(chat_id=CHAT_ID, text=f"Bot is running. Signals sent today: {signals_sent_today}/{MAX_SIGNALS}")

# ----------------------
# MAIN LOOP
# ----------------------
def run_bot():
    global signals_sent_today
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('status', status))

    updater.start_polling()

    while True:
        now = datetime.datetime.now()
        if now.hour == 0 and now.minute == 0:
            signals_sent_today = 0  # Reset daily counter

        df = get_data()
        last = df.iloc[-1]
        prev = df.iloc[-2]

        # BUY condition
        if last['EMA_FAST'] > last['EMA_SLOW'] and prev['EMA_FAST'] <= prev['EMA_SLOW'] and last['RSI'] > 55:
            entry = last['Close']
            sl = entry - 1.5
            tp = entry + 3.0
            send_signal("🟢 BUY", entry, sl, tp)

        # SELL condition
        if last['EMA_FAST'] < last['EMA_SLOW'] and prev['EMA_FAST'] >= prev['EMA_SLOW'] and last['RSI'] < 45:
            entry = last['Close']
            sl = entry + 1.5
            tp = entry - 3.0
            send_signal("🔴 SELL", entry, sl, tp)

        time.sleep(60)

if __name__ == "__main__":
    run_bot()
