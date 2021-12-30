#! /usr/bin/env python3

import unittest

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
      'expire': 'datum-noch-gültig'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_abgelaufen(self):
    with open('testfiles/ausweis-abgelaufen.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': 'datum-abgelaufen'
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
      'expire': 'datum-noch-gültig'
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
        'duedate': 'faelligkeitsdatum1',
        'fromlib': 'bibnamelang1',
        'title': 'medientyp1: titel1 abgeschnitt'
      },
      {
        'duedate': 'faelligkeitsdatum2',
        'fromlib': 'bibnamelang2',
        'title': 'medientyp2: titel2 abgeschnitt'
      }
    ]
    self.assertEqual(iteminfo, expectediteminfo)

if __name__ == '__main__':
  unittest.main()
