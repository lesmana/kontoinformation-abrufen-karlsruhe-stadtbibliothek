#!/usr/bin/env python

import sys
import requests
import bs4
import pprint
import time
import datetime
import types
import argparse
import json

url = 'https://opac.karlsruhe.de/opax/user.C'

class KaException(Exception):
  pass

def getargv(argv):
  class HandleUsername(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
      secretfilename = values if values.endswith('.secret') else values + '.secret'
      namespace.secretfilename = secretfilename
  parser = argparse.ArgumentParser()
  parser.add_argument('username',
        action=HandleUsername,
        help='name of user to get info for')
  parser.add_argument('--dumphtml',
        action='store_true',
        help='just dump html instead extracting info')
  parser.add_argument('--printjson',
        action='store_true',
        help='print info in json instead human friendly plain text')
  parser.add_argument('--fromhtmlfile',
        dest='htmlfilename',
        help='get info from html file instead of website on live internets'
          ' (this is mainly for testing)')
  args = parser.parse_args()
  args.url = url
  return args

def getsoupfromfile(htmlfilename):
  try:
    with open(htmlfilename) as openfile:
      soup = bs4.BeautifulSoup(openfile.read(), 'html.parser')
  except:
    raise KaException('error trying to read html from file', htmlfilename)
  return soup

def getlogindata(secretfilename):
  try:
    with open(secretfilename) as openfile:
      username, password = openfile.read().splitlines()
  except:
    raise KaException('error trying to read credentials from file', secretfilename)
  return username, password

def getsoupfrominternets(secretfilename, url):
  username, password = getlogindata(secretfilename)
  session = requests.Session()
  formdata = {
    'LANG': 'de',
    'FUNC': 'medk',
    'BENUTZER': username,
    'PASSWORD': password
  }
  response = session.post(url, data=formdata)
  if response.status_code != 200:
    raise KaException('response status code not 200', response)
  soup = bs4.BeautifulSoup(response.content, 'html.parser')
  return soup

def gettables(soup):
  tables = soup.find_all('table', attrs={'class': 'tab21'})
  usersoup = tables[0]
  if len(tables) == 1:
    itemsoup = None
  elif len(tables) == 2:
    itemsoup = tables[1]
  else:
    raise KaException('unexpected number of tables', tables)
  return usersoup, itemsoup

def getuserinfo(usersoup):
  userinfo = {}
  infotds = usersoup.find_all('td')
  name = infotds[1].get_text(strip=True)
  userinfo['name'] = name
  feestr = infotds[2].get_text(strip=True)
  if feestr != '':
    fee, _ = feestr.split()
    userinfo['fee'] = fee
  expirestr = infotds[5].get_text(strip=True)
  _, expire = expirestr.split()
  userinfo['expire'] = expire
  return userinfo

def getoneiteminfo(itemtr):
  itemtds = itemtr.find_all('td')
  duedate = itemtds[3].get_text(strip=True)
  fromlib = itemtds[5].font['title']
  title = itemtds[7].get_text(strip=True).translate(str.maketrans('', '', '\r\n'))
  item = {
    'duedate': duedate,
    'fromlib': fromlib,
    'title': title
  }
  return item

def getiteminfo(itemsoup):
  iteminfo = []
  itemtrs = itemsoup.find_all('tr')
  for itemtr in itemtrs[2:]:
    item = getoneiteminfo(itemtr)
    iteminfo.append(item)
  return iteminfo

def getinfoexcept(soup):
  usersoup, itemsoup = gettables(soup)
  userinfo = getuserinfo(usersoup)
  if itemsoup is not None:
    iteminfo = getiteminfo(itemsoup)
  else:
    iteminfo = []
  info = {'user': userinfo, 'items': iteminfo}
  return info

def dumpfile(name, text):
  with open(name, 'wt') as openfile:
    openfile.write(text)

def getinfo(soup, today):
  try:
    return getinfoexcept(soup)
  except Exception as e:
    now = today.isoformat(timespec='seconds')
    name = f'ka-bib-info-error-dump-{now}.html'
    text = soup.prettify()
    dumpfile(name, text)
    raise KaException(
          f'error getting info from soup. '
          f'html written to file {name}') from e

def printuserinfo(userinfo, today):
  name = userinfo['name']
  yield f'name: {name}'
  if 'fee' in userinfo:
    fee = userinfo['fee']
    yield f'gebühren: {fee} €'
  expire = userinfo["expire"]
  delta = datetime.datetime.strptime(expire, '%d.%m.%Y') - today
  if delta.days < 0:
    yield f'ausweis ist seit {abs(delta.days)} tagen abgelaufen ({expire})'
  elif delta.days < 14:
    yield f'ausweis läuft in {delta.days} tagen ab ({expire})'

def printoneiteminfo(item, today):
  title = item['title']
  yield f'titel: {title}'
  duedate = item["duedate"]
  delta = datetime.datetime.strptime(duedate, '%d.%m.%Y') - today
  if delta.days < 0:
    yield f'überfällig seit {abs(delta.days)} tagen ({duedate})'
  else:
    yield f'fällig in {delta.days} tagen ({duedate})'
  fromlib = item['fromlib']
  yield f'bib: {fromlib}'

def printiteminfo(iteminfo, today):
  yield ''
  if len(iteminfo) == 0:
    yield 'nichts ausgeliehen'
    return
  for item in iteminfo:
    yield from printoneiteminfo(item, today)
    yield ''

def printinfogen(info, today):
  userinfo = info['user']
  yield from printuserinfo(userinfo, today)
  iteminfo = info['items']
  yield from printiteminfo(iteminfo, today)

def printinfoexcept(info, today):
  for line in printinfogen(info, today):
    print(line)

def printinfo(info, today, soup):
  try:
    printinfoexcept(info, today)
  except Exception as e:
    now = today.isoformat(timespec='seconds')
    htmlname = f'ka-bib-info-error-dump-{now}.html'
    htmltext = soup.prettify()
    dumpfile(htmlname, htmltext)
    jsonname = f'ka-bib-info-error-dump-{now}.json'
    jsontext = json.dumps(info, indent=4)
    dumpfile(jsonname, jsontext)
    raise KaException(
          f'error printing info from json. '
          f'html written to file {htmlname}. '
          f'json written to file {jsonname}.'
          ) from e

def main():
  options = getargv(sys.argv)
  if options.htmlfilename is not None:
    soup = getsoupfromfile(options.htmlfilename)
  else:
    soup = getsoupfrominternets(options.secretfilename, options.url)
  if options.dumphtml:
    print(soup.prettify())
    return
  today = datetime.datetime.today()
  info = getinfo(soup, today)
  if options.printjson:
    print(json.dumps(info, indent=4))
    return
  printinfo(info, today, soup)

if __name__ == '__main__':
  main()
