from datetime import datetime
import json
import logging
import requests

import bybit

class BybitExchange:
    def __init__(self, test=True):
        self.test = test

        logging.basicConfig(filename="./app/logs/bybit_exchange.log", format='%(asctime)s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("-----------------------------------")
        self.logger.info("Starting Bybit exchange client")

        #get keys and authenticate with the bybit api
        api_key, api_secret = self.get_keys()
        self.client = bybit.bybit(test=self.test, api_key=api_key, api_secret=api_secret)

    def get_keys(self):
        with open('./app/secret/bybit_keys.json', 'r') as f:
            key_config = json.load(f)

        key_dict = key_config['testnet'] if self.test else key_config['mainnet']        
        return key_dict['api_key'], key_dict['api_secret']
    
    def get_time(self):
        time_url = 'https://api-testnet.bybit.com/v2/public/time'
        response = requests.get(time_url).json()
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_time: returned {response.get('time_now')}")
            return response.get('time_now')
        else:
            self.logger.error("[BYBIT CLIENT] get_time: bad request")
    
    def get_timestamp(self):
        response = self.client.Market.Market_orderbook(symbol="BTCUSD").result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_timestamp: returned {response.get('time_now')}")
            return response.get('time_now')
        else:
            self.logger.error("[BYBIT CLIENT] get_timestamp: bad request")

    def get_equity(self, coin):
        kwargs = { "coin": coin }
        response = self.client.Wallet.Wallet_getBalance(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_equity: returned {response.get('result').get(coin).get('available_balance')}")
            return response.get('result').get(coin).get('equity')
        else:
            self.logger.error("[BYBIT CLIENT] get_equity: bad request")

    def get_available_balance(self, coin):
        kwargs = { "coin": coin }
        response = self.client.Wallet.Wallet_getBalance(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_available_balance: returned {response.get('result').get(coin).get('available_balance')}")
            return response.get('result').get(coin).get('available_balance')
        else:
            self.logger.error("[BYBIT CLIENT] get_availlable_balance: bad request")

    def get_market_price(self, symbol):
        kwargs = { "symbol": symbol }
        response = self.client.Market.Market_symbolInfo(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_market_price: returned {response.get('result')[0].get('mark_price')}")
            return float(response.get('result')[0].get('mark_price'))
        else:
            self.logger.error("[BYBIT CLIENT] get_market_price: bad request")
        
    def get_position(self, symbol):
        kwargs = {"symbol" : symbol}
        response = self.client.Positions.Positions_myPosition(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_position: returned {response.get('result')}")
            return response.get('result')
        else:
            self.logger.error("[BYBIT CLIENT] get_position: bad request")

    def get_leverage(self, symbol):
        response = self.client.Positions.Positions_userLeverage().result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_leverage: returned {response.get('result').get(symbol).get('leverage')}")
            return response.get('result').get(symbol).get('leverage')
        else:
            self.logger.error("[BYBIT CLIENT] get_leverage: bad request")

    def get_active_orders(self, symbol):
        response = self.client.Order.Order_getOrders(symbol=symbol).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_active_orders: returned {response.get('result').get('data')}")
            return response.get('result').get("data")
        else:
            self.logger.error("[BYBIT CLIENT] get_active_orders: bad request")
    
    def get_fund_records(self, symbol):
        response = self.client.Wallet.Wallet_getRecords(limit="10").result()[0]        
        if response.get('ret_msg') == 'ok':
            self.logger.info(f"[BYBIT CLIENT] get_fund_records: returned {response.get('result')}")
            return response.get('result').get('data')
        else:
            self.logger.error("[BYBIT CLIENT] get_fund_records: bad request")

    def get_closed_pnl(self, symbol, start_time):
        response = self.client.Positions.Positions_closePnlRecords(symbol=symbol, start_time=start_time).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_closed_pnl: returned {response.get('result')}")
            return response.get('result').get('data')
        else:
            self.logger.error("[BYBIT CLIENT] get_closed_pnl: bad request")
        
    def get_executed_orders(self, symbol, start_time):
        response = self.client.Execution.Execution_getTrades(symbol=symbol, start_time=start_time).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_executed_orders: returned {response.get('result')}")
            return response.get('result').get('trade_list')
        else:
            self.logger.error("[BYBIT CLIENT] get_executed_orders: bad request")