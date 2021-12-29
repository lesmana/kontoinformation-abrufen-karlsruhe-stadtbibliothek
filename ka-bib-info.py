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

def getargv(argv):
  class HandleUsername(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
      secretfilename = values if values.endswith('.secret') else values + '.secret'
      namespace.secretfilename = secretfilename
  parser = argparse.ArgumentParser()
  parser.add_argument('username', action=HandleUsername,
        help='name of user to get info for')
  parser.add_argument('--dumphtml', action='store_true',
        help='just dump html instead extracting info')
  parser.add_argument('--printjson', action='store_true',
        help='print info in json instead human friendly plain text')
  args = parser.parse_args()
  args.url = url
  return args

def getlogindata(secretfilename):
  try:
    with open(secretfilename) as secretfile:
      username, password = secretfile.read().splitlines()
  except:
    raise Exception('error trying to read credentials from file', secretfilename)
  return username, password

def gethtmlstr(username, password, url):
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
  return response.content

def gettables(htmlstr):
  soup = bs4.BeautifulSoup(htmlstr, 'html.parser')
  tables = soup.find_all('table', attrs={'class': 'tab21'})
  usertable = tables[0]
  if len(tables) == 1:
    itemtable = None
  elif len(tables) == 2:
    itemtable = tables[1]
  else:
    raise Exception('unexpected number of tables', tables)
  return usertable, itemtable

def dumphtml(usertable, itemtable):
  print(usertable.prettify())
  if itemtable is not None:
    print(itemtable.prettify())

def getuserinfo(usertable):
  userinfo = {}
  infotds = usertable.find_all('td')
  name = ''.join(infotds[1].stripped_strings)
  userinfo['name'] = name
  fee = ''.join(infotds[2].stripped_strings)
  if fee != '':
    userinfo['fee'] = fee
  validity = ''.join(infotds[5].stripped_strings)
  _, validity = validity.split()
  userinfo['validity'] = validity
  return userinfo

def getiteminfo(itemtable):
  iteminfo = []
  itemtrs = itemtable.find_all('tr')
  for itemtr in itemtrs[2:]:
    #print(itemtr.prettify())
    itemtds = itemtr.find_all('td')
    duedate = itemtds[3].string
    fromlib = itemtds[5].font['title']
    title = itemtds[7].string.replace('\r\n', ' ')
    item = {
      'duedate': duedate,
      'fromlib': fromlib,
      'title': title
    }
    iteminfo.append(item)
  return iteminfo

def getinfo(usertable, itemtable):
  userinfo = getuserinfo(usertable)
  if itemtable is not None:
    iteminfo = getiteminfo(itemtable)
  else:
    iteminfo = []
  info = {'user': userinfo, 'item': iteminfo}
  return info

def printjson(info):
  print(json.dumps(info, indent=4))

def printinfo(info, today):
  userinfo = info['user']
  print('name', userinfo['name'])
  if 'fee' in userinfo:
    print('gebühren', userinfo['fee'])
  validity = userinfo["validity"]
  delta = datetime.datetime.strptime(validity, '%d.%m.%Y') - today
  if delta.days < 0:
    print(f'ausweis abgelaufen ({validity})')
    print(f'in tagen: {delta.days}')
  elif delta.days < 14:
    print(f'ausweis läuft bald ab ({validity})')
    print(f'in tagen: {delta.days}')

  if len(info['item']) == 0:
    print('nichts ausgeliehen')
  else:
    for item in info['item']:
      duedate = item["duedate"]
      delta = datetime.datetime.strptime(duedate, '%d.%m.%Y') - today
      print(f'fällig: {duedate} (in tagen: {delta.days})')
      print('bib:', item['fromlib'])
      print('titel:', item['title'])

def main():
  options = getargv(sys.argv)
  username, password = getlogindata(options.secretfilename)
  htmlstr = gethtmlstr(username, password, options.url)
  usertable, itemtable = gettables(htmlstr)
  if options.dumphtml:
    dumphtml(usertable, itemtable)
    return
  info = getinfo(usertable, itemtable)
  if options.printjson:
    printjson(info)
    return
  today = datetime.datetime.today()
  printinfo(info, today)

if __name__ == '__main__':
  main()
