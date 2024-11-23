from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
# import pandas as pd
from config import CMC_API_KEY

def get_all():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
      'start':'1',
      'limit':'5000',
      'convert':'USD'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    session = Session()
    session.headers.update(headers)

    try:
      response = session.get(url, params=params)
      data = json.loads(response.text)
      # with open('/DATA/harshit_2311ai52/tgBot/coinmarketcap.json', 'w') as f:
      #     json.dump(data, f, indent=2)
      return(data['data'])
      # for x in data['data']:
      #     print(x['symbol'],x['quote']['USD']['price'])
      # with open('example.json', 'w') as f:
      #     json.dump(data, f, indent=2)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      return(e)

