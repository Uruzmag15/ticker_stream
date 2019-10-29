# python 3.7

import asyncio
import websockets
import time
import json


binance_uri = 'wss://stream.binance.com:9443/ws/btcusdt@bookTicker'
okex_uri = 'wss://real.okex.com:8443/ws/v3/spot/ticker:BTC-USDT'


async def get_avg_price(resp):
    bb = float(resp.get('b'))      # best bid price
    ba = float(resp.get('a'))  # best ask price
    if bb and ba:
        return (bb + ba)/2
    return 0


async def listen_to_binance(uri):
    async with websockets.connect(uri) as socket:
        while True:
            response = await socket.recv()
            resp_dict = json.loads(response)
            print('{} "{}" {} avg_price: $ {}'.format(time.strftime('%H:%M:%S'),
                                                     'BINANCE',
                                                     resp_dict.get('s'),
                                                     await get_avg_price(resp_dict)))
            # print(resp_dict)
            await asyncio.sleep(1)      # optional


async def listen_to_binance2(uri):
    async with websockets.connect(uri) as socket:
        while True:
            response = await socket.recv()
            resp_dict = json.loads(response)
            print('2222 {} "{}" {} avg_price: $ {}'.format(time.strftime('%H:%M:%S'),
                                                     'BINANCE',
                                                     resp_dict.get('s'),
                                                     await get_avg_price(resp_dict)))
            # print(resp_dict)
            await asyncio.sleep(1)      # optional


async def main():
    task1 = asyncio.create_task(listen_to_binance(binance_uri))
    task2 = asyncio.create_task(listen_to_binance2(binance_uri))

    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    print('Started...')
    asyncio.run(main())
