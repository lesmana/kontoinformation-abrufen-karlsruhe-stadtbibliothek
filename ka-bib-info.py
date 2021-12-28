#!/usr/bin/env python

import sys
import requests
import bs4
import pprint
import time
import datetime
import types
import argparse

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
  args = parser.parse_args()
  args.url = url
  return args

def getlogindata(secretfilename):
  try:
    with open(secretfilename) as secretfile:
      username, password = secretfile.read().splitlines()
  except:
    raise Exception('error trying to read credentials from file', secretfilename)
    sys.exit(1)
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
    borrowtable = None
  elif len(tables) == 2:
    borrowtable = tables[1]
  else:
    raise Exception('unexpected number of tables', tables)
  return usertable, borrowtable

def dumphtml(usertable, borrowtable):
  print(usertable.prettify())
  if borrowtable is not None:
    print(borrowtable.prettify())

def printuserinfo(usertable, today):
  infotds = usertable.find_all('td')
  name = ''.join(infotds[1].stripped_strings)
  print('name', name)
  fee = ''.join(infotds[2].stripped_strings)
  if fee != '':
    print('gebühren', fee)
  validity = ''.join(infotds[5].stripped_strings)
  _, validity = validity.split()
  delta = datetime.datetime.strptime(validity, '%d.%m.%Y') - today
  #print(validity)
  #print(delta.days)
  if delta.days < 0:
    print(f'ausweis abgelaufen ({validity})')
    print(f'in tagen: {delta.days}')
  elif delta.days < 14:
    print(f'ausweis läuft bald ab ({validity})')
    print(f'in tagen: {delta.days}')

def printborrowinfo(borrowtable, today):
  borrowtrs = borrowtable.find_all('tr')
  for borrowtr in borrowtrs[2:]:
    #print(borrowtr.prettify())
    borrowtds = borrowtr.find_all('td')
    duedate = borrowtds[3].string
    delta = datetime.datetime.strptime(duedate, '%d.%m.%Y') - today
    fromlib = borrowtds[5].font['title']
    title = borrowtds[7].string.replace('\r\n', ' ')
    print(f'fällig: {duedate} (in tagen: {delta.days})')
    print('bib:', fromlib)
    print('titel:', title)

def printinfo(usertable, borrowtable, today):
  printuserinfo(usertable, today)
  if borrowtable is not None:
    printborrowinfo(borrowtable, today)
  else:
    print('nichts ausgeliehen')

def main():
  options = getargv(sys.argv)
  username, password = getlogindata(options.secretfilename)
  htmlstr = gethtmlstr(username, password, options.url)
  usertable, borrowtable = gettables(htmlstr)
  if options.dumphtml:
    dumphtml(usertable, borrowtable)
  else:
    today = datetime.datetime.today()
    printinfo(usertable, borrowtable, today)

if __name__ == '__main__':
  main()
