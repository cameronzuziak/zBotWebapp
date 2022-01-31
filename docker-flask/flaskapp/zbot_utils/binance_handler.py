import json
from binance.client import Client
from binance.enums import *
from zbot_utils.twil_handler import sms_send
import math
from config import *


def get_current_positions(api_key, sec_key):
    client = Client(api_key, sec_key, tld='us')
    account=client.get_account()
    portfolio_total = 0
    assets=[] 
    for coin in account['balances']:
        amt=float(coin['free']) + float(coin['locked'])
        if(amt>0):
            asst = str(coin['asset'])
            if not asst == ("USDT" or "BUSD" or "USDC"):
                asst_pair = asst + "USDT"
                try:
                    z = client.get_avg_price(symbol=asst_pair)
                except Exception:
                    try:
                        asst_pair = asst + "USD"
                        z = client.get_avg_price(symbol=asst_pair)
                    except Exception:
                        print(asst_pair)
                value = amt*float(z['price'])
            else:
                value = amt
            if value > 1:
                value = round(value,2)
                portfolio_total += value 
                x={ 
                "asset": asst,
                "amnt": str(amt),
                "value": value,
                }
                assets.append(x)
        port = [round(portfolio_total,2), assets]
    return port


def get_historical_data(api_key, sec_key, SYMB, TIME_INT):
    client = Client(api_key, sec_key, tld='us')
    time_interval = {
        "1m" : Client.KLINE_INTERVAL_1MINUTE,
        "3m" : Client.KLINE_INTERVAL_3MINUTE,
        "5m" : Client.KLINE_INTERVAL_5MINUTE,
        "15m" : Client.KLINE_INTERVAL_15MINUTE,
        "30m" : Client.KLINE_INTERVAL_30MINUTE,
        "1h" : Client.KLINE_INTERVAL_1HOUR,
        "4h" : Client.KLINE_INTERVAL_4HOUR,
        "6h" : Client.KLINE_INTERVAL_6HOUR,
        "12h" : Client.KLINE_INTERVAL_12HOUR,
        "1d" : Client.KLINE_INTERVAL_1DAY,
        "1w" : Client.KLINE_INTERVAL_1WEEK,
        "1M" : Client.KLINE_INTERVAL_1MONTH
    }
    
    candles = client.get_klines(symbol=SYMB, interval=time_interval[TIME_INT], limit=1000)
    x = {"candles": candles}
    json_object = json.dumps(x)
    return candles


def get_buy_quantity(symbol_stripped, symbol_tokens, API_KEY, SEC_KEY):
    client = Client(API_KEY, SEC_KEY, tld='us')
    last = client.get_symbol_ticker(symbol = symbol_stripped)
    last = float(last['price'])
    balance = client.get_asset_balance(symbol_tokens[1])
    balance = float(balance['free'])
    coin_size = str(last).split('.')
    coin_size = len(coin_size[0])
    # .9 to account for slippage and rounding errors. 
    quantity = (balance / last) * .9
    if(coin_size - 1) == 0:
        quantity = round(quantity) 
    else:
       quantity = round(quantity, coin_size-1) 
    return quantity


def get_sell_quantity(symbol_stripped, symbol_tokens, API_KEY, SEC_KEY):
    client = Client(API_KEY, SEC_KEY, tld='us')
    balanceS = client.get_asset_balance(symbol_tokens[0])
    balanceS = balanceS['free']
    balanceS = float(balanceS) 
    print(balanceS)
    last = client.get_symbol_ticker(symbol = symbol_stripped)
    last = float(last['price'])
    coin_size = str(last).split('.')
    coin_size = len(coin_size[0])
    print(coin_size)

    if coin_size == 1:
        balanceS = math.floor(balanceS)

    elif coin_size <= 3:
        coin_size -= 1
        n = 10**coin_size
        balanceS = math.floor(balanceS*n)/n


    elif int(coin_size) > 3:
        coin_size += 1
        print(coin_size)
        n = 10**coin_size
        balanceS = math.floor(balanceS*n)/n

    return balanceS


def buy_order(symbol_stripped, symbol_tokens, API_KEY, SEC_KEY):
    client = Client(API_KEY, SEC_KEY, tld='us')
    quantity = get_buy_quantity(symbol_stripped, symbol_tokens)
    try:
        
        order = client.create_order(symbol=symbol_stripped, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity)
        price = order['fills'][0]['price']
        msg = "bought in at price %s " % str(price)
        sms_send(msg)
        return(order['fills'][0]['price'])

    except Exception as e:
        sms_send("an exception occured in buy order - {}".format(e))
        return False
    

def sell_limit(symbol_stripped, symbol_tokens, percent_take, price, API_KEY, SEC_KEY):
    client = Client(API_KEY, SEC_KEY, tld='us')
    quantity = get_sell_quantity(symbol_stripped, symbol_tokens)
    price += price*percent_take
    price = (f'{price:.6f}')
    print (price)
    print(quantity)
    try:
        order = client.create_order(
                symbol = symbol_stripped, 
                side = SIDE_SELL, 
                type = ORDER_TYPE_LIMIT, 
                timeInForce = TIME_IN_FORCE_GTC, 
                quantity = quantity, 
                price = price)
    except Exception as e:
        sms_send("an exception occured in sell limit order- {}".format(e))
        return False
    return order
    

def stop_limit_order(symbol_stripped, symbol_tokens, price, percent_take, API_KEY, SEC_KEY): 
    client = Client(API_KEY, SEC_KEY, tld='us')
    price = float(price)*float(percent_take)
    quantity = client.get_asset_balance(symbol_tokens[1])
    stopPrice = price - price*.06
    try:
        #print("sending order")
        sms_send("sending order")
        order = client.create_order(
            symbol = symbol_stripped, 
            side = SIDE_BUY, 
            type = ORDER_TYPE_STOP_LOSS_LIMIT, 
            timeInForce = TIME_IN_FORCE_GTC, 
            quantity = quantity, 
            price = price, 
            stopPrice = stopPrice)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False    
    return True


def cancel_and_close(symbol_stripped, symbol_tokens, API_KEY, SEC_KEY):
    client = Client(API_KEY, SEC_KEY, tld='us')
    client._delete('openOrders', True, data={'symbol': symbol_stripped})
    balance = get_sell_quantity(symbol_stripped, symbol_tokens)
    #balance = float(balance['free'])
    try:
        #print("sending order")
        sms_send("sending order")
        if len(client.get_open_orders()) == 0:
            order = client.create_order(symbol=symbol_stripped, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=balance)
        print(order)
    except Exception as e:
        #print("an exception occured - {}".format(e))
        sms_send("an exception occured - {}".format(e))
        return False

    sms_send('stop loss triggered at %s' % order['fills'][0]['price'])    
    return True

