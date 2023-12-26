import requests
import os

BITLY_TOKEN = os.environ.get('BITLY_TOKEN')

link_example = 'https://dev.bitly.com'
# https://www.udemy.com/course/the-ultimate-guide-about-creating-telegram-bots-with-python/learn/lecture/15914506#reviews
short_link_example = 'https://bitly.is/48uc6rI'
# https://bit.ly/478WSY5


def shorten_url(link=link_example, token=BITLY_TOKEN):
    if link.startswith('https://'):
        link_url = link
    else:
        link_url = 'https://' + link
    url = 'https://api-ssl.bitly.com/v4/shorten'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    data = {"long_url": link_url}
    response = requests.post(url=url, headers=headers, json=data)
    bitly_data = response.json()
    if response.ok:
        return bitly_data['link']
    else:
        return 0


def get_clicks_count(link=short_link_example, token=BITLY_TOKEN):
    if link.startswith('https://'):
        link_url = link[6:]
    else:
        link_url = link
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{link_url}/clicks/summary'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    params = (
        ('unit', 'month'),
        ('units', '1'),
    )
    response = requests.get(url=url, headers=headers, params=params)
    bitly_data = response.json()
    if response.ok:
        # print(bitly_data)
        # print(bitly_data['total_clicks'])
        return bitly_data['total_clicks']
    else:
        return 'Bad URL, please retry!'


# get_clicks_count()
# shorten_url()
