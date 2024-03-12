#!/usr/bin/env python
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import time
from rich import print


config_logging(logging, logging.ERROR)

KEY = ""
SECRET = ""

um_futures_client = UMFutures(
    key=KEY, secret=SECRET, base_url="https://testnet.binancefuture.com"
)


def format_error(error):
    return f"{error.status_code=}, {error.error_code=}, {error.error_message=}"


def sell(price):
    response = None
    try:
        response = um_futures_client.new_order(
            symbol="XMRUSDT",
            side="SELL",
            type="LIMIT",
            quantity=0.05,
            timeInForce="GTC",
            price=price,
        )
        logging.info(response)
    except ClientError as error:
        logging.error(format_error(error))
    return response


def buy(price):
    response = None
    try:
        response = um_futures_client.new_order(
            symbol="XMRUSDT",
            side="BUY",
            type="LIMIT",
            quantity=0.05,
            timeInForce="GTC",
            price=price,
        )
        logging.info(response)
    except ClientError as error:
        logging.error(format_error(error))
    return response


def get_mark_price(symbol):
    response = None
    try:
        response = um_futures_client.mark_price(symbol=symbol)
        logging.info(response)
        return response["markPrice"]
    except ClientError as error:
        logging.error(format_error(error))
    return response


def new_batch_order(orders):
    response = None
    try:
        response = um_futures_client.new_batch_order(orders)
        logging.info(response)
    except ClientError as error:
        logging.error(format_error(error))
    return response


def get_orders(symbol, side, quantity, center_price, multipliers):
    quantities = [1.0, 2.0, 6.0, 12.0, 48.0]
    prices = [center_price * m for m in multipliers]
    prices_and_quantities = list(zip(prices, quantities))
    orders = []
    for p, q in prices_and_quantities:
        price = str(round(p, 3))
        quantity = str(round(q, 3))
        orders.append(
            {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "quantity": quantity,
                "timeInForce": "GTC",
                "price": price,
            }
        )

    return orders


def submit_orders(symbol, side, quantity, center_price, multipliers):
    orders = get_orders(symbol, side, quantity, center_price, multipliers)
    return new_batch_order(orders)


def get_open_orders(symbol):
    response = None
    try:
        response = um_futures_client.get_orders(symbol=symbol, recvWindow=2000)
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(format_error(error))
    return response


def main():
    print("start")
    buy_order_id = None
    sell_order_id = None
    while True:
        try:
            mark_price = float(get_mark_price("XMRUSDT"))
            open_orders = get_open_orders("XMRUSDT")
            open_orders_num = len(open_orders)
            if False:  # open_orders_num == 0:
                quantity = 1.0
                distances = [0.5, 1, 2, 4, 8]
                multipliers = [1 - (d / 100) for d in distances]
                submit_orders("XMRUSDT", "BUY", quantity, mark_price, multipliers)
                multipliers = [1 + (d / 100) for d in distances]
                submit_orders("XMRUSDT", "SELL", quantity, mark_price, multipliers)
            else:
                if open_orders_num > 0:
                    sell_orders_ids = [
                        i["orderId"] for i in open_orders if i["side"] == "SELL"
                    ]
                    if sell_order_id is None or sell_order_id not in sell_orders_ids:
                        sell_order_id = sell(round(mark_price * 1.01, 2))["orderId"]
                    buy_orders_ids = [
                        i["orderId"] for i in open_orders if i["side"] == "BUY"
                    ]
                    if buy_order_id is None or buy_order_id not in buy_orders_ids:
                        buy_order_id = buy(round(mark_price * 0.99, 2))["orderId"]
                # pass
            time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
