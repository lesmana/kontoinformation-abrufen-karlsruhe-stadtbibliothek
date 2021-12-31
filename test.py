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

  def test_ueberfaellig(self):
    with open('testfiles/ausleih-ueberfaellig.html') as openfile:
      htmlstr = openfile.read()
    itemtable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    iteminfo = t.getiteminfo(itemtable)
    expectediteminfo = [
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
      'name voller name'
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
      'name voller name',
      'ausweis läuft bald ab (25.04.2021)',
      'in tagen: 5'
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
      'name voller name',
      'ausweis abgelaufen (15.04.2021)',
      'in tagen: -5'
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
      'name voller name',
      'gebühren 3,50 €'
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
      'name voller name',
      'gebühren 3,50 €',
      'ausweis abgelaufen (15.04.2021)',
      'in tagen: -5'
    ]
    self.assertEqual(printed, expectedprinted)

if __name__ == '__main__':
  unittest.main()
