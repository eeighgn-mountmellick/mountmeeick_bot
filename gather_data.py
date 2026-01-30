import pandas as pd
import requests
import os

STATIONS = {"14121": "Manor Road", "14120": "Chapel Street"}
FLOOD_THRESHOLD = 0.8  # Meters
RISE_THRESHOLD = 0.1   # 10cm per hour

def send_alert(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message})

def process():
    for st_id, st_name in STATIONS.items():
        for sensor in ["0001", "0002"]: # Level and Temp
            url = f"http://waterlevel.ie/data/day/{st_id}_{sensor}.csv"
            file = f"history_{st_id}_{sensor}.csv"
            
            try:
                new_df = pd.read_csv(url, skipinitialspace=True, skiprows=6)
                new_df.columns = ['datetime', 'value']
                
                if os.path.exists(file):
                    old_df = pd.read_csv(file)
                    df = pd.concat([old_df, new_df]).drop_duplicates(subset=['datetime'])
                else:
                    df = new_df
                
                df = df.sort_values('datetime')
                df.to_csv(file, index=False)

                # Alerts only for Water Level (0001)
                if sensor == "0001" and len(df) > 4:
                    latest_val = df['value'].iloc[-1]
                    rate_1hr = latest_val - df['value'].iloc[-5]
                    pred_2hr = latest_val + (rate_1hr * 2)

                    if latest_val >= FLOOD_THRESHOLD:
                        send_alert(f"🔴 FLOOD: {st_name} is at {latest_val}m!")
                    elif rate_1hr >= RISE_THRESHOLD:
                        send_alert(f"⚠️ RAPID RISE: {st_name} +{round(rate_1hr*100,1)}cm/hr!")
                    elif pred_2hr >= FLOOD_THRESHOLD:
                        send_alert(f"🔍 FORECAST: {st_name} predicted to hit threshold in 2hrs.")

            except Exception as e: print(f"Error {st_id}: {e}")

if __name__ == "__main__":
    process()
