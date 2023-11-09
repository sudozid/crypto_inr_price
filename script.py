import json
import requests
import csv
from datetime import datetime
import pytz
import numpy as np
import time
import statistics

timezone = pytz.timezone('Asia/Kolkata')

# Function to fetch median P2P price from Binance
def get_binance_p2p_median_price():
    currency = "INR"
    p2p_url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json"}

    payload = {
        "fiat": currency,
        "page": 1,
        "rows": 10,
        "tradeType": "BUY",
        "asset": "USDT",
        "countries": [],
        "proMerchantAds": False,
        "shieldMerchantAds": False,
        "publisherType": "merchant",
        "payTypes": [],
        "classifies": ["mass", "profession"]
    }

    price_list = []

    def fetch_prices(page):
        try:
            payload['page'] = page
            response = requests.post(p2p_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['total'] == 0:
                return False
            for ad in data['data']:
                try:
                    price = float(ad['adv']['price'])
                    price_list.append(price)
                except (KeyError, ValueError):
                    pass
            return True
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return False
        except Exception as err:
            print(f"An error occurred: {err}")
            return False

    page = 1
    while fetch_prices(page):
        page += 1

    if price_list:
        median_price = statistics.median(price_list)
        return median_price
    else:
        return None

def extractor(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                # Parse the JSON data
                data = response.json()
                return data
            except json.JSONDecodeError:
                print(f"Failed to decode JSON. Response content: {response.text}")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}. Response content: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None



def get_median_price_from_offers(url):
    data = extractor(url)
    if data and 'data' in data:
        fiat_prices = [offer['fiatPricePerBtc'] for offer in data['data'] if isinstance(offer.get('fiatPricePerBtc'), (int, float))]
        if fiat_prices:
            return np.median(fiat_prices)
    return ""

def get_wazirx_p2p_rate():
    data = extractor("https://x.wazirx.com/wazirx-falcon/api/v1.0/p2p/order-book?market=usdtinr&limit=10")
    if data:
        # Extract the bids and asks
        bids = data['bids']
        asks = data['asks']
        # Find the highest bid and the lowest ask
        highest_bid = max(bids, key=lambda x: float(x[0]))[0]
        lowest_ask = min(asks, key=lambda x: float(x[0]))[0]
        return (float(highest_bid) + float(lowest_ask)) / 2
    else:
        return ""

def white_rate():
    data = extractor(
        "https://api.freecurrencyapi.com/v1/latest?apikey=API&currencies=INR")
    if data:
        return data['data']['INR']
    else:
        return ""

def write_to_csv(data):
    with open('rates.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    while True:
        # Get the current datetime
        now = datetime.now(timezone)
        # Format the date and time, separated by a comma
        date_time_string = now.strftime("%Y-%m-%d,%H:%M:%S")

        # Get WAX rate
        wazirx_rate = get_wazirx_p2p_rate()
        official_rate = white_rate()

        # Get median price from Paxful offers
        paxful_rate = get_median_price_from_offers("https://paxful.com/rest/v1/offers?transformResponse=camelCase&withFavorites=false&crypto_currency_id=4&is_payment_method_localized=0&visitor_country_has_changed=false&visitor_country_iso=SG&group=bank-transfers&fiat-min=10000&currency=INR&payment-method%5B0%5D=with-any-payment-method&type=buy")

        #Get rates from Binance P2P
        binance_rate=get_binance_p2p_median_price()

        # Write to CSV with the median price in between
        write_to_csv([date_time_string, binance_rate, wazirx_rate, paxful_rate, official_rate])

        # Wait for one hour
        time.sleep(3600)

if __name__ == "__main__":
    main()
