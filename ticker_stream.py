# python 3.7

import asyncio
import websockets
import time
import json
import zlib


binance_url = 'wss://stream.binance.com:9443/ws/btcusdt@bookTicker'
okex_url = 'wss://real.okex.com:8443/ws/v3'

okex_params = {"op": "subscribe", "args": ["spot/ticker:BTC-USDT"]}
okex_params_json = json.dumps(okex_params)


def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


async def get_avg_price(price1, price2):
    bb = float(price1)
    ba = float(price2)
    if bb and ba:
        return (bb + ba)/2
    return 0


async def parse_binance(resp_dict):
    data = {}
    price1 = resp_dict.get('b')     # best bid price
    price2 = resp_dict.get('a')     # best ask price
    data['market'] = 'BINANCE'
    instrumen = resp_dict.get('s')
    data['instrument'] = '{}-{}'.format(instrumen[:3], instrumen[3:])
    data['avg_price'] = await get_avg_price(price1, price2)
    return data


async def parse_okex(resp_dict):
    data = {}
    try:
        resp_dict_data = resp_dict.get('data')[0]
        price1 = resp_dict_data.get('best_bid')
        price2 = resp_dict_data.get('best_ask')
        data['market'] = 'OKEX'
        data['instrument'] = resp_dict_data.get('instrument_id')
        data['avg_price'] = await get_avg_price(price1, price2)
        return data
    except IndexError as e:
        return str(e)


async def print_result(url, resp_dict):
    if 'binance' in url:
        parsed_data = await parse_binance(resp_dict)
    else:
        parsed_data = await parse_okex(resp_dict)

    if type(parsed_data) is dict:
        print('{} "{}" {} avg_price: $ {}'.format(time.strftime('%H:%M:%S'),
                                              parsed_data.get('market'),
                                              parsed_data.get('instrument'),
                                              parsed_data.get('avg_price')))
    else:
        print(parsed_data)


async def start_listening_to_binance(url):
    async with websockets.connect(url) as socket:
        while True:
            response = await socket.recv()

            resp_dict = json.loads(response)

            await print_result(url, resp_dict)
            await asyncio.sleep(1)      # optional


async def start_listening_to_okex(url):
    async with websockets.connect(url) as socket:

        await socket.send(okex_params_json)
        await socket.recv()

        while True:
            response = await socket.recv()

            inflated_resp = inflate(response)
            resp_dict = json.loads(inflated_resp)

            await print_result(url, resp_dict)
            await asyncio.sleep(1)      # optional


async def main():
    task1 = asyncio.create_task(start_listening_to_binance(binance_url))
    task2 = asyncio.create_task(start_listening_to_okex(okex_url))

    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    print('Listening is started...')
    asyncio.run(main())
