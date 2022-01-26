#! /usr/bin/env python3

# ka-bib-info
# Copyright Lesmana Zimmer lesmana@gmx.de
# Licensed under GNU AGPL version 3 or later
# https://www.gnu.org/licenses/agpl-3.0.html

import unittest
import datetime

from unittest import mock

import bs4

t = __import__('ka-bib-info')

# some html test data in files because long
# also in files can see diff using diff tools

class TestGetUserInfo(unittest.TestCase):

  def test_normal(self):
    with open('testfiles/ausweis-normal.html') as openfile:
      htmlstr = openfile.read()
    usersoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(usersoup)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': '01.11.2021'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_gebuehren(self):
    with open('testfiles/ausweis-gebuehren.html') as openfile:
      htmlstr = openfile.read()
    usersoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(usersoup)
    expecteduserinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '01.11.2021'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_ausleihe(self):
    # parsing ausleihe not implemented yet
    with open('testfiles/ausweis-ausleihe.html') as openfile:
      htmlstr = openfile.read()
    usersoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(usersoup)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': '01.11.2021'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_emptyhtml(self):
    # test error handling of code
    # if html not containing expected tags
    htmlstr = '<table></table>'
    usersoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    with self.assertRaises(IndexError):
      _ = t.getuserinfo(usersoup)

class TestGetItemInfo(unittest.TestCase):

  def test_normal(self):
    with open('testfiles/ausleih-normal.html') as openfile:
      htmlstr = openfile.read()
    itemsoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemsoup)
    expectediteminfo = [
      {
        'duedate': '01.05.2021',
        'fromlib': 'bibnamelang1',
        'title': 'medientyp1: titel1 abgeschnitt'
      },
      {
        'duedate': '02.05.2021',
        'fromlib': 'bibnamelang2',
        'title': 'medientyp2: titel2 abgeschnitt'
      }
    ]
    self.assertEqual(iteminfo, expectediteminfo)

  def test_missingitems(self):
    # this not realistic error
    # because either items are present
    # or the entire table is not present
    # still it tests robustness of code
    # in this case code throws no error
    # returns empty list instead
    with open('testfiles/ausleih-missingitems.html') as openfile:
      htmlstr = openfile.read()
    itemsoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemsoup)
    expectediteminfo = []
    self.assertEqual(iteminfo, expectediteminfo)

  def test_emptyhtml(self):
    # this is also not realistic error
    # but test robustness of code nonetheless
    htmlstr = '<table></table>'
    itemsoup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemsoup)
    expectediteminfo = []
    self.assertEqual(iteminfo, expectediteminfo)

class TestGetInfo(unittest.TestCase):

  def test_normal(self):
    with open('testfiles/alles-normal.html') as openfile:
      htmlstr = openfile.read()
    soup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    # second parameter is today
    # which is only relevant in case of error
    info = t.getinfo(soup, None)
    expectedinfo = {
      'user': {
        'name': 'voller name',
        'expire': '01.11.2021'
      },
      'items': [
        {
          'duedate': '01.05.2021',
          'fromlib': 'bibnamelang1',
          'title': 'medientyp1: titel1 abgeschnitt'
        },
        {
          'duedate': '02.05.2021',
          'fromlib': 'bibnamelang2',
          'title': 'medientyp2: titel2 abgeschnitt'
        }
      ]
    }
    self.maxDiff = None
    self.assertEqual(info, expectedinfo)

  def test_error(self):
    # test error handling
    # in case html does not contain expected tags
    # error handling dumps the html to file
    # it mocks open using mock_open
    htmlstr = '<html></html>'
    soup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    mock_open = mock.mock_open()
    with mock.patch('__main__.t.open', mock_open):
      with self.assertRaises(t.KaException):
        _ = t.getinfo(soup, today)
    self.maxDiff = None
    self.assertEqual(mock_open.mock_calls, [
        mock.call('ka-bib-info-error-dump-20210420000000.html', 'wt'),
        mock.call().__enter__(),
        mock.call().write('<html>\n</html>'),
        mock.call().__exit__(None, None, None)])

class TestPrintUserInfo(unittest.TestCase):

  def test_normal(self):
    userinfo = {
      'name': 'voller name',
      'expire': '01.11.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printuserinfo(userinfo, today))
    expectedlines = [
      'name: voller name'
    ]
    self.assertEqual(lines, expectedlines)

  def test_läuftbaldab(self):
    userinfo = {
      'name': 'voller name',
      'expire': '25.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printuserinfo(userinfo, today))
    expectedlines = [
      'name: voller name',
      'ausweis läuft in 5 tagen ab (25.04.2021)'
    ]
    self.assertEqual(lines, expectedlines)

  def test_abgelaufen(self):
    userinfo = {
      'name': 'voller name',
      'expire': '15.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printuserinfo(userinfo, today))
    expectedlines = [
      'name: voller name',
      'ausweis ist seit 5 tagen abgelaufen (15.04.2021)'
    ]
    self.assertEqual(lines, expectedlines)

  def test_gebuehren(self):
    userinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '01.11.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printuserinfo(userinfo, today))
    expectedlines = [
      'name: voller name',
      'gebühren: 3,50 €'
    ]
    self.assertEqual(lines, expectedlines)

  def test_gebuehren_abgelaufen(self):
    userinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '15.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printuserinfo(userinfo, today))
    expectedlines = [
      'name: voller name',
      'gebühren: 3,50 €',
      'ausweis ist seit 5 tagen abgelaufen (15.04.2021)'
    ]
    self.assertEqual(lines, expectedlines)

  def test_empty(self):
    # this is not realistic error
    # because preceding code wouldn't return empty dict
    # this just tests error handling of code
    userinfo = {}
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    with self.assertRaises(KeyError):
      _ = list(t.printuserinfo(userinfo, today))

class TestPrintItemInfo(unittest.TestCase):

  def test_normal(self):
    iteminfo = [
      {
        'duedate': '01.05.2021',
        'fromlib': 'bibnamelang1',
        'title': 'medientyp1: titel1 abgeschnitt'
      },
      {
        'duedate': '02.05.2021',
        'fromlib': 'bibnamelang2',
        'title': 'medientyp2: titel2 abgeschnitt'
      }
    ]
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printiteminfo(iteminfo, today))
    expectedlines = [
      '',
      'titel: medientyp1: titel1 abgeschnitt',
      'fällig in 11 tagen (01.05.2021)',
      'bib: bibnamelang1',
      '',
      'titel: medientyp2: titel2 abgeschnitt',
      'fällig in 12 tagen (02.05.2021)',
      'bib: bibnamelang2',
      ''
   ]
    self.assertEqual(lines, expectedlines)

  def test_ueberfaellig(self):
    iteminfo = [
      {
        'duedate': '01.04.2021',
        'fromlib': 'bibnamelang1',
        'title': 'medientyp1: titel1 abgeschnitt'
      },
      {
        'duedate': '02.04.2021',
        'fromlib': 'bibnamelang2',
        'title': 'medientyp2: titel2 abgeschnitt'
      }
    ]
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printiteminfo(iteminfo, today))
    expectedlines = [
      '',
      'titel: medientyp1: titel1 abgeschnitt',
      'überfällig seit 19 tagen (01.04.2021)',
      'bib: bibnamelang1',
      '',
      'titel: medientyp2: titel2 abgeschnitt',
      'überfällig seit 18 tagen (02.04.2021)',
      'bib: bibnamelang2',
      ''
   ]
    self.assertEqual(lines, expectedlines)

  def test_empty(self):
    iteminfo = []
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printiteminfo(iteminfo, today))
    expectedlines = [
      '',
      'nichts ausgeliehen'
    ]
    self.assertEqual(lines, expectedlines)

  def test_empty2(self):
    # this is not realistic error
    # because preceding code wouldn't return empty dict
    # this just tests error handling of code
    iteminfo = [{}]
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    with self.assertRaises(KeyError):
      _ = list(t.printiteminfo(iteminfo, today))

class TestPrintInfo(unittest.TestCase):

  def test_normal(self):
    info = {
      'user': {
        'name': 'voller name',
        'expire': '01.11.2021'
      },
      'items': [
        {
          'duedate': '01.05.2021',
          'fromlib': 'bibnamelang1',
          'title': 'medientyp1: titel1 abgeschnitt'
        },
        {
          'duedate': '02.05.2021',
          'fromlib': 'bibnamelang2',
          'title': 'medientyp2: titel2 abgeschnitt'
        }
      ]
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    lines = list(t.printinfo(info, today))
    expectedlines = [
      'name: voller name',
      '',
      'titel: medientyp1: titel1 abgeschnitt',
      'fällig in 11 tagen (01.05.2021)',
      'bib: bibnamelang1',
      '',
      'titel: medientyp2: titel2 abgeschnitt',
      'fällig in 12 tagen (02.05.2021)',
      'bib: bibnamelang2',
      ''
    ]
    self.maxDiff = None
    self.assertEqual(lines, expectedlines)

  def test_handleexception(self):
    htmlstr = '<html></html>'
    soup = bs4.BeautifulSoup(htmlstr, 'html.parser')
    info = {}
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    mock_open = mock.mock_open()
    with mock.patch('__main__.t.open', mock_open):
      htmlname, jsonname = t.printinfohandleexception(info, today, soup)
    self.maxDiff = None
    #print(mock_open.mock_calls)
    self.assertEqual(mock_open.mock_calls, [
        mock.call('ka-bib-info-error-dump-20210420000000.html', 'wt'),
        mock.call().__enter__(),
        mock.call().write('<html>\n</html>'),
        mock.call().__exit__(None, None, None),
        mock.call('ka-bib-info-error-dump-20210420000000.json', 'wt'),
        mock.call().__enter__(),
        mock.call().write('{}'),
        mock.call().__exit__(None, None, None)])
    self.assertEqual(htmlname, 'ka-bib-info-error-dump-20210420000000.html')
    self.assertEqual(jsonname, 'ka-bib-info-error-dump-20210420000000.json')

if __name__ == '__main__':
  unittest.main()
