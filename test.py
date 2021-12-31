#! /usr/bin/env python3

import unittest
import datetime

import bs4

t = __import__('ka-bib-info')

class TestGetUserInfo(unittest.TestCase):

  def test_ok(self):
    with open('testfiles/ausweis-ok.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': '01.11.2021'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_gebuehren(self):
    with open('testfiles/ausweis-gebuehren.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '01.11.2021'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_emptyhtml(self):
    htmlstr = ''
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    with self.assertRaises(IndexError):
      _ = t.getuserinfo(infotable)

class TestGetItemInfo(unittest.TestCase):

  def test_ok(self):
    with open('testfiles/ausleih-ok.html') as openfile:
      htmlstr = openfile.read()
    itemtable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemtable)
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
    itemtable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemtable)
    expectediteminfo = []
    self.assertEqual(iteminfo, expectediteminfo)

  def test_emptyhtml(self):
    htmlstr = ''
    itemtable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemtable)
    expectediteminfo = []
    self.assertEqual(iteminfo, expectediteminfo)

class TestPrintUserInfo(unittest.TestCase):

  def test_ok(self):
    userinfo = {
      'name': 'voller name',
      'expire': '01.11.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printuserinfo(userinfo, today))
    expectedprinted = [
      'name: voller name'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_läuftbaldab(self):
    userinfo = {
      'name': 'voller name',
      'expire': '25.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printuserinfo(userinfo, today))
    expectedprinted = [
      'name: voller name',
      'ausweis läuft in 5 tagen ab (25.04.2021)'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_abgelaufen(self):
    userinfo = {
      'name': 'voller name',
      'expire': '15.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printuserinfo(userinfo, today))
    expectedprinted = [
      'name: voller name',
      'ausweis ist seit 5 tagen abgelaufen (15.04.2021)'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_gebuehren(self):
    userinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '01.11.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printuserinfo(userinfo, today))
    expectedprinted = [
      'name: voller name',
      'gebühren: 3,50 €'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_gebuehren_abgelaufen(self):
    userinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': '15.04.2021'
    }
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printuserinfo(userinfo, today))
    expectedprinted = [
      'name: voller name',
      'gebühren: 3,50 €',
      'ausweis ist seit 5 tagen abgelaufen (15.04.2021)'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_empty(self):
    userinfo = {}
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    with self.assertRaises(KeyError):
      _ = list(t.printuserinfo(userinfo, today))

class TestPrintItemInfo(unittest.TestCase):

  def test_ok(self):
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
    printed = list(t.printiteminfo(iteminfo, today))
    expectedprinted = [
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
    self.assertEqual(printed, expectedprinted)

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
    printed = list(t.printiteminfo(iteminfo, today))
    expectedprinted = [
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
    self.assertEqual(printed, expectedprinted)

  def test_empty(self):
    iteminfo = []
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    printed = list(t.printiteminfo(iteminfo, today))
    expectedprinted = [
      '',
      'nichts ausgeliehen'
    ]
    self.assertEqual(printed, expectedprinted)

  def test_empty2(self):
    # this is not realistic error
    # because preceding code wouldn't return empty dict
    # this just tests error handling of code
    iteminfo = [{}]
    today = datetime.datetime.strptime('20.04.2021', '%d.%m.%Y')
    with self.assertRaises(KeyError):
      _ = list(t.printiteminfo(iteminfo, today))

if __name__ == '__main__':
  unittest.main()
