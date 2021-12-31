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
import tempfile

url = 'https://opac.karlsruhe.de/opax/user.C'

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
        help='get info from html file instead of website on live internets')
  args = parser.parse_args()
  args.url = url
  return args

def getsoupfromfile(htmlfilename):
  try:
    with open(htmlfilename) as openfile:
      soup = bs4.BeautifulSoup(openfile.read(), 'html.parser')
  except:
    raise Exception('error trying to read html from file', htmlfilename)
  return soup

def getlogindata(secretfilename):
  try:
    with open(secretfilename) as secretfile:
      username, password = secretfile.read().splitlines()
  except:
    raise Exception('error trying to read credentials from file', secretfilename)
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
    raise Exception('response status code not 200', response)
  soup = bs4.BeautifulSoup(response.content, 'html.parser')
  return soup

def dumphtml(soup):
  print(soup.prettify())

def gettables(soup):
  tables = soup.find_all('table', attrs={'class': 'tab21'})
  usertable = tables[0]
  if len(tables) == 1:
    itemtable = None
  elif len(tables) == 2:
    itemtable = tables[1]
  else:
    raise Exception('unexpected number of tables', tables)
  return usertable, itemtable

def getuserinfo(usertable):
  userinfo = {}
  infotds = usertable.find_all('td')
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

def getiteminfo(itemtable):
  iteminfo = []
  itemtrs = itemtable.find_all('tr')
  for itemtr in itemtrs[2:]:
    itemtds = itemtr.find_all('td')
    duedate = itemtds[3].get_text(strip=True)
    fromlib = itemtds[5].font['title']
    title = itemtds[7].get_text(strip=True).translate(str.maketrans('', '', '\r\n'))
    item = {
      'duedate': duedate,
      'fromlib': fromlib,
      'title': title
    }
    iteminfo.append(item)
  return iteminfo

def getinfoexcept(soup):
  usertable, itemtable = gettables(soup)
  userinfo = getuserinfo(usertable)
  if itemtable is not None:
    iteminfo = getiteminfo(itemtable)
  else:
    iteminfo = []
  info = {'user': userinfo, 'items': iteminfo}
  return info

def getinfo(soup):
  try:
    return getinfoexcept(soup)
  except Exception:
    fd, name = tempfile.mkstemp(prefix='ka-bib-info-error-html-dump-', suffix='.html', dir='.', text=True)
    with open(fd, 'wt') as openfile:
      openfile.write(soup.prettify())
    print('error getting info from soup', file=sys.stderr)
    print('html written to file', name, file=sys.stderr)
    raise

def printjson(info):
  print(json.dumps(info, indent=4))

def printuserinfo(userinfo, today):
  name = userinfo['name']
  print('name', name)
  if 'fee' in userinfo:
    fee = userinfo['fee']
    print('gebühren', fee, '€')
  expire = userinfo["expire"]
  delta = datetime.datetime.strptime(expire, '%d.%m.%Y') - today
  if delta.days < 0:
    print(f'ausweis abgelaufen ({expire})')
    print(f'in tagen: {delta.days}')
  elif delta.days < 14:
    print(f'ausweis läuft bald ab ({expire})')
    print(f'in tagen: {delta.days}')

def printiteminfo(iteminfo, today):
  if len(iteminfo) == 0:
    print('nichts ausgeliehen')
  else:
    for item in iteminfo:
      duedate = item["duedate"]
      delta = datetime.datetime.strptime(duedate, '%d.%m.%Y') - today
      print(f'fällig: {duedate} (in tagen: {delta.days})')
      fromlib = item['fromlib']
      print('bib:', fromlib)
      title = item['title']
      print('titel:', title)

def printinfo(info, today):
  userinfo = info['user']
  printuserinfo(userinfo, today)
  iteminfo = info['items']
  printiteminfo(iteminfo, today)

def main():
  options = getargv(sys.argv)
  if options.htmlfilename is not None:
    soup = getsoupfromfile(options.htmlfilename)
  else:
    soup = getsoupfrominternets(options.secretfilename, options.url)
  if options.dumphtml:
    dumphtml(soup)
    return
  info = getinfo(soup)
  if options.printjson:
    printjson(info)
    return
  today = datetime.datetime.today()
  printinfo(info, today)

if __name__ == '__main__':
  main()
