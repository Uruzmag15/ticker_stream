okex_uri = 'wss://real.okex.com:8443/ws/v3/spot/ticker:BTC-USDT'

# python 3.7

import asyncio
import websockets
import time
import json


async def get_avg_price(price1, price2):
    bb = float(price1)
    ba = float(price2)
    if bb and ba:
        return (bb + ba)/2
    return 0


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


async def print_result(uri, resp_dict):
    parsed_data = await parse_okex(resp_dict)

    if type(parsed_data) is dict:
        print('{} "{}" {} avg_price: $ {}'.format(time.strftime('%H:%M:%S'),
                                              parsed_data.get('market'),
                                              parsed_data.get('instrument'),
                                              parsed_data.get('avg_price')))
    else:
        print(parsed_data)


async def start_listening_to(uri):
    async with websockets.connect(uri) as socket:
        while True:
            response = await socket.recv()
            resp_dict = json.loads(response)

            await print_result(uri, resp_dict)
            # print(resp_dict)
            await asyncio.sleep(1)      # optional


async def main():
    task1 = asyncio.create_task(start_listening_to(okex_uri))

    await asyncio.gather(task1)


if __name__ == '__main__':
    print('Started...')
    asyncio.run(main())