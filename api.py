import requests
import json
import urllib.parse
import os
import time
from bs4 import BeautifulSoup

URL = 'https://news.ycombinator.com'
headers = {"Content-Type": "application/x-www-form-urlencoded",
            "Access-Control-Allow-Origin": "*"}


def get_maxitem():
    r = requests.get('https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty')
    return r.json()

def get_item(id):
     url = 'https://hacker-news.firebaseio.com/v0/item/{0}.json?print=pretty'.format(id)
     r = requests.get(url)
     return r.json()

def get_story(id):
    item = get_item(id)
    if item['type'] == 'story':
        return item
    return None

def print_item(item):
    print('-'*20, id, '-'*20)
    if 'title' in item: print(item['title'])
    if 'text' in item: print(item['text'])
    if 'url' in item: print(item['url'])
    print('{0}/item?id={1}'.format(URL, item['id']))

session = requests.session()

def encode(s):
    return urllib.parse.quote(str(s), safe='~()*!.\'')

def get_data(b):
    body = []
    for k,v in b.items():
        body += ['{0}={1}'.format(encode(k), encode(v))]
    return '&'.join(body)

def login(user, pw):
    b = { 'acct': user, 'pw': pw, 'goto': 'news'}
    body = get_data(b)
    request = session.post(URL + '/login', data=body, headers=headers)

def get_HMAC(id):
    request = session.get(URL + '/item?id={0}'.format(id), headers=headers)
    soup = BeautifulSoup(request.text, features="html.parser")
    try:
        value = soup.find('input', {'name': 'hmac'}).get('value')
        return value
    except:
        pass
    return None

def reply(id, text):
    hmac = get_HMAC(id)
    b = { 'parent': id, 'hmac': hmac, 'text': text, 'goto': 'item?id={0}'.format(id)}
    body = get_data(b)
    request = session.post(URL + '/comment', data=body, headers=headers)

def hn_reply(item):
    print('Would you like to comment? [y]')
    yn = input()
    if yn == 'y':
        user = os.environ.get('HN_US')
        pw = os.environ.get('HN_PW')
        login(user, pw)
        print('Comment please ...')
        msg = input()
        reply(item['id'], msg)

keywords = ['learning', 'analysis', 'neural', 'deep', 'ask hn', 'machine', 'musk', 'tesla', 'pattern', 'django', 'celery']

maxid = get_maxitem()
last_id = maxid - 40

while True:
    maxid = get_maxitem()
    for id in range(last_id, maxid):
        print(id)
        item = get_story(id)
        if item:
            skip = True
            for k in keywords:
                if 'title' in item and k in item['title']:
                    skip = False
            if skip:
                print('.')
                continue
            print_item(item)
            hn_reply(item)
    last_id = maxid
    time.sleep(30)
