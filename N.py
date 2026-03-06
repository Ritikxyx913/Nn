#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import sys
import os

# ================= CONFIG =================
TELEGRAM_BOT_TOKEN = "7527768602:AAEcx-4NUnO5_K3UDQQNjSiyos8ss1VSgo4"
TELEGRAM_CHAT_ID = "-1002481129519"

# Direct API (without proxy)
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts={}"
POLL_INTERVAL = 6

# ================= STATE =================
history_data = []
last_period = None
level = 1
current_side = None
math_mode = False

def get_label(num):
    return "𝐁𝐈𝐆" if int(num) >= 5 else "𝐒𝐌𝐀𝐋𝐋"

def random_from_side(side):
    return random.choice([5,6,7,8,9]) if "BIG" in side else random.choice([0,1,2,3,4])

def send_message(text):
    """Send to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"📱 Telegram: {r.status_code}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def fetch_data():
    """Fetch from API"""
    try:
        ts = int(time.time() * 1000)
        url = API_URL.format(ts)
        print(f"🌐 Fetching: {url[:50]}...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            if "data" in data and "list" in data["data"]:
                print(f"✅ Got {len(data['data']['list'])} items")
                return data["data"]["list"]
        print(f"❌ API error: {r.status_code}")
        return []
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return []

def math_formula():
    if len(history_data) < 10:
        return random.randint(0,9)
    try:
        curr = int(history_data[-1]["actual"])
        sec = int(history_data[-2]["actual"])
        tenth = int(history_data[-10]["actual"])
        return (abs(curr - sec) + tenth) % 10
    except:
        return random.randint(0,9)

# ================= MAIN =================
def main():
    global last_period, level, current_side, math_mode
    
    print("="*50)
    print("🔥 BOT STARTING ON RAIPACK")
    print("="*50)
    
    send_message("🤖 Bot started on Raipack!")
    
    while True:
        try:
            issues = fetch_data()
            if not issues:
                time.sleep(POLL_INTERVAL)
                continue
            
            latest = issues[0]
            period = str(latest["issueNumber"])
            number = int(latest["number"])
            
            if period != last_period:
                actual_label = get_label(number)
                
                # Previous result
                if history_data:
                    prev = history_data[-1]
                    if prev["status"] == "Pending":
                        prev["actual"] = number
                        if prev["prediction"] == actual_label:
                            prev["status"] = "WIN"
                            level = 1
                            math_mode = False
                        else:
                            prev["status"] = "LOSS"
                            level += 1
                
                # Level system
                if level == 1:
                    current_side = actual_label
                elif level == 2:
                    current_side = "𝐒𝐌𝐀𝐋𝐋" if "BIG" in current_side else "𝐁𝐈𝐆"
                elif level >= 4:
                    math_mode = True
                
                # New prediction
                if math_mode:
                    ai_number = math_formula()
                    current_side = get_label(ai_number)
                else:
                    ai_number = random_from_side(current_side)
                
                next_period = str(int(period) + 1)
                
                history_data.append({
                    "period": next_period,
                    "prediction": current_side,
                    "status": "Pending",
                    "actual": None
                })
                
                msg = f"🎯 <b>{next_period}</b>\n📊 {current_side}\n🔢 {ai_number}\n⚙ Level {level}"
                send_message(msg)
                
                last_period = period
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            sys.exit(0)
        except Exception as e:
            print(f"⚠️ {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
