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

def submit(title, link):

    b = { 'title': title, 'url': link, 'goto': 'news'}
    body = get_data(b)
    request = session.post(URL + '/submit', data=body, headers=headers)
    print(request)
    print(request.text)
    print(request.status_code)


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

def hn_submit(title, link):
    user = os.environ.get('HN_US')
    pw = os.environ.get('HN_PW')
    login(user, pw)
    submit(title, link)


def comment_mode():
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
                    if 'title' in item and k in item['title'].lower():
                        skip = False
                if skip:
                    print('.')
                    continue
                print_item(item)
                hn_reply(item)
        last_id = maxid
        time.sleep(30)

def get_posts():
    #return {'[R] Natural Environment Benchmarks for Reinforcement Learning: we challenge the RL research community to develop more robust algorithms that meet high standards of evaluation': 'https://arxiv.org/abs/1811.06032', '[R] Rethinking ImageNet Pre-training': 'https://arxiv.org/abs/1811.08883', '[R] GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism (new ImageNet SOTA)': 'https://arxiv.org/abs/1811.06965', 'GAN-QP: A Novel GAN Framework without Gradient Vanishing and Lipschitz Constraint': 'https://arxiv.org/abs/1811.07296', '[R] Practical Bayesian Learning of Neural Networks via Adaptive Subgradient Methods': 'https://arxiv.org/abs/1811.03679'}

    r = requests.get('https://www.reddit.com/r/MachineLearning/new')

    soup = BeautifulSoup(r.text, features="html.parser")
    posts = {}
    for ul in soup.find_all('article'):
        titile, link = None, None
        for h in ul.find_all('h2'):
            title = h.text
        for a in ul.find_all('a', {'target':'_blank'}):
            #print('***', a.get('href'))
            if 'reddit' not in a.get('href'):
                link = a.get('href')
        #print(title, link)
        if title is not None and link is not None:
            posts[title] = link
    #print(posts)
    if len(posts) == 0:
        print(r.text)
    return posts

def prepare_title(title):
    title = title.replace('[R]', '')
    title = title.strip()
    if len(title) > 80:
        arr = title.split()
        title = []
        cnt = 0
        for a in arr:
            cnt += len(a)+1
            if cnt < 80:
                title += [a]
        title = ' '.join(title)
    return title

def repost_mode():
    print('*** REPOST MODE ***')
    hist = {}
    while True:
        print('*** get post')
        posts = get_posts()

        for title, link in posts.items():
            if title not in hist:
                print('-'*50)
                print(title)
                hist[title] = link
                new_title = prepare_title(title)
                print(new_title)
                print(link)


        time.sleep(300)

repost_mode()
