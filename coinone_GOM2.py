""" 코인원 GOM2[고머니2] """

import time
import random
from datetime import datetime, timedelta
import hmac
import json
import base64
import hashlib
import httplib2
import simplejson
from random import randint

EXCHANGE = "코인원"  # 거래소명
SYMBOL = "gom2"  # 코인 심볼: 소문자로 작성

MIN_AMOUNT = 1000  # 매매수량(최소수량 ~)
MAX_AMOUNT = 2000  # 매매수량(~ 최대수량)

START_TIME = 10  # 시간(START_TIME ~) (초)
END_TIME = 20  # 시간(~ END_TIME 사이) (초)

# Decimals: 거래소에 코인 호가가 소수점 몇째 자리수로 되어있는지 확인
DECIMALS = 2


### 아래는 건드리지 말 것 ###
while True:
    # 트레이딩 타임
    t = datetime.now()  # + timedelta(hours=9)
    trading_time = t.strftime("%Y/%m/%d %H:%M:%S")
    try:
        print("")
        print("------------------------------------------------------------------------")
        # API 키
        ACCESS_TOKEN = ""
        SECRET_KEY = ""


        def get_encoded_payload(payload):
            payload[u'nonce'] = int(time.time() * 1000)

            dumped_json = simplejson.dumps(payload).encode()
            encoded_json = base64.b64encode(dumped_json)
            return encoded_json


        def get_signature(encoded_payload, secret_key):
            signature = hmac.new(secret_key.upper().encode(), encoded_payload, hashlib.sha512)
            return signature.hexdigest()


        def get_response(url, payload):
            encoded_payload = get_encoded_payload(payload)
            headers = {
                'Content-type': 'application/json',
                'X-COINONE-PAYLOAD': encoded_payload,
                'X-COINONE-SIGNATURE': get_signature(encoded_payload, SECRET_KEY)
            }
            http = httplib2.Http()
            response, content = http.request(url, 'GET', headers=headers, body=encoded_payload)
            return content


        def post_response(url, payload):
            encoded_payload = get_encoded_payload(payload)
            headers = {
                'Content-type': 'application/json',
                'X-COINONE-PAYLOAD': encoded_payload,
                'X-COINONE-SIGNATURE': get_signature(encoded_payload, SECRET_KEY)
            }
            http = httplib2.Http()
            response, content = http.request(url, 'POST', headers=headers, body=encoded_payload)
            return content


        def coin_order_book(currency):
            url = 'https://api.coinone.co.kr/orderbook/?currency={}&format=json'.format(currency)
            payload = {
                "access_token": ACCESS_TOKEN,
            }
            content = get_response(url, payload)
            return content


        def coin_balance():
            url = 'https://api.coinone.co.kr/v2/account/balance/'
            payload = {
                "access_token": ACCESS_TOKEN,
            }
            content = post_response(url, payload)
            return content


        def coin_limit_buy(price, qty, currency):  # 매수함수- price : 가격, qty : 수량, currency: 코인
            url = 'https://api.coinone.co.kr/v2/order/limit_buy/'
            payload = {
                "access_token": ACCESS_TOKEN,
                "price": price,
                "qty": qty,
                "currency": currency
            }
            content = post_response(url, payload)
            return content


        def coin_limit_sell(price, qty, currency):  # 매도함수 - price : 가격, qty : 수량, currency: 코인
            url = 'https://api.coinone.co.kr/v2/order/limit_sell/'
            payload = {
                "access_token": ACCESS_TOKEN,
                "price": price,
                "qty": qty,
                "currency": currency
            }
            content = post_response(url, payload)
            return content


        # 함수 실행 - coin_balance()
        my_coin_balance = coin_balance()
        my_gom2_quantity = json.loads(my_coin_balance.decode("utf-8"))
        my_gom2_quantity = my_gom2_quantity[f"{SYMBOL}"]
        my_gom2_avail = my_gom2_quantity["avail"]

        # 함수 실행 - coin_order_book() (bid -> 매수, ask -> 매도)
        my_coin_order_book = coin_order_book(f"{SYMBOL}")
        bid_ask_price = json.loads(my_coin_order_book.decode("utf-8"))  # 매수/매도 전체 호가
        bid_price = bid_ask_price["bid"]  # 전체 매수호가
        ask_price = bid_ask_price["ask"]  # 전체 매도호가

        # 전체 매도호가 리스트
        ask_list = []
        for aa in ask_price:
            aa = dict(aa)
            ask_list.append(aa['price'])

        # 현재 최저 매도 호가
        min_ask_price = ask_list[0]
        min_ask_price = float(min_ask_price)
        print("현재 최저 매도 호가 :", min_ask_price, f"{SYMBOL}", type(min_ask_price))

        # 전체 매수호가 리스트
        bid_list = []
        for aa in bid_price:
            aa = dict(aa)
            bid_list.append(aa['price'])

        # 현재 최저 매수 호가
        max_bid_price = bid_list[0]
        max_bid_price = float(max_bid_price)
        print("현재 최고 매수 호가 :", max_bid_price, f"{SYMBOL}")

        gap = round(min_ask_price - max_bid_price, DECIMALS)

        if DECIMALS == 3:
            gapDecimals = 0.002
        elif DECIMALS == 2:
            gapDecimals = 0.02
        elif DECIMALS == 1:
            gapDecimals = 0.2

        if gap >= float(gapDecimals):  # 호가 갭 차이 >= gapDecimals
            if DECIMALS == 3:
                floats = 0.001
            elif DECIMALS == 2:
                floats = 0.01
            elif DECIMALS == 1:
                floats = 0.1

            bidGap = round(max_bid_price + floats, DECIMALS)  # 최고 매수호가 바로 위
            askGap = round(min_ask_price - floats, DECIMALS)  # 최소 매도호가 바로 아래

            # 거래 1
            price = round(random.uniform(bidGap, askGap), DECIMALS)
            buy_sell_quantity = randint(MIN_AMOUNT, MAX_AMOUNT)
            first_decimal = "0."
            last_decimal = str(randint(1, 9999))
            final_decimal = float(first_decimal + last_decimal)
            amount = float(buy_sell_quantity) + final_decimal
            sell = coin_limit_sell(price, amount, f"{SYMBOL}")  # 최종 매도로직 -> coin_limit_buy(가격, 수량, 코인)
            buy = coin_limit_buy(price, amount, f"{SYMBOL}")  # 최종 매수로직 -> coin_limit_buy(가격, 수량, 코인)
            print(f"거래1 매도 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {sell}")
            print(f"거래1 매수 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {buy}")
            print("")

            time.sleep(0.3)

            # 거래 2
            price = round(random.uniform(bidGap, askGap), DECIMALS)
            buy_sell_quantity = randint(MIN_AMOUNT, MAX_AMOUNT)
            first_decimal = "0."
            last_decimal = str(randint(1, 9999))
            final_decimal = float(first_decimal + last_decimal)
            amount = float(buy_sell_quantity) + final_decimal
            sell = coin_limit_sell(price, amount, f"{SYMBOL}")  # 최종 매도로직 -> coin_limit_buy(가격, 수량, 코인)
            buy = coin_limit_buy(price, amount, f"{SYMBOL}")  # 최종 매수로직 -> coin_limit_buy(가격, 수량, 코인)
            print(f"거래2 매도 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {sell}")
            print(f"거래2 매수 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {buy}")
            print("")
            time.sleep(0.3)

            # 거래 3
            price = round(random.uniform(bidGap, askGap), DECIMALS)
            buy_sell_quantity = randint(MIN_AMOUNT, MAX_AMOUNT)
            first_decimal = "0."
            last_decimal = str(randint(1, 9999))
            final_decimal = float(first_decimal + last_decimal)
            amount = float(buy_sell_quantity) + final_decimal
            sell = coin_limit_sell(price, amount, f"{SYMBOL}")  # 최종 매도로직 -> coin_limit_buy(가격, 수량, 코인)
            buy = coin_limit_buy(price, amount, f"{SYMBOL}")  # 최종 매수로직 -> coin_limit_buy(가격, 수량, 코인)
            print(f"거래3 매도 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {sell}")
            print(f"거래3 매수 - {price}원, 수량: {amount} {SYMBOL.upper()}, history: {buy}")

            print(f"거래 시간: {trading_time}")
        else:
            print("거래 시간: 호가가 꽉 차 있음")
            print(f"신청시간: {trading_time}")
            pass

    except Exception as e:
        print(f"문제 발생: {e}")
        pass

    time_sleep = randint(START_TIME, END_TIME)
    print(f"{EXCHANGE} {SYMBOL} {time_sleep}초 후...")
    time.sleep(time_sleep)