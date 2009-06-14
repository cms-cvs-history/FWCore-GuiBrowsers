#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *

from TestDataAccessor import *
from Vispa.Main.FindAlgorithm import *
from Vispa.Main import Profiling

class TestFindDialog(object):
    def __init__(self):
        self._label=""
        self._properties=[]
        self._scripts=[]
        self._caseSensitive=False
        self._exactMatch=False

    def label(self):
        return self._label
    
    def properties(self):
        return self._properties
    
    def scripts(self):
        return self._scripts
    
    def caseSensitive(self):
        return self._caseSensitive

    def exactMatch(self):
        return self._exactMatch

    def test1(self):
        self._label="container1"
        self._properties=[]
        self._caseSensitive=False
        self._exactMatch=False
        
    def test2(self):
        self._label="Particle1"
        self._properties=[]
        self._caseSensitive=False
        self._exactMatch=False

    def test3(self):
        self._label=""
        self._properties=[("label","")]
        self._caseSensitive=False
        self._exactMatch=False

    def test4(self):
        self._label=""
        self._properties=[("label","particle")]
        self._caseSensitive=False
        self._exactMatch=False

    def test5(self):
        self._label=""
        self._properties=[("Label","particle1")]
        self._caseSensitive=True
        self._exactMatch=True

    def test6(self):
        self._label=""
        self._properties=[("Label","Particle1")]
        self._caseSensitive=True
        self._exactMatch=True

    def test7(self):
        self._label=""
        self._properties=[("Labe","particle1")]
        self._caseSensitive=True
        self._exactMatch=True

    def test8(self):
        self._label=""
        self._properties=[("Label","pa"),("Label","particle6")]
        self._caseSensitive=False
        self._exactMatch=False

    def test9(self):
        self._label=""
        self._properties=[("Label","particle1"),("","")]
        self._caseSensitive=True
        self._exactMatch=True

    def test10(self):
        self._label=""
        self._properties=[]
        self._scripts=["object.Label=='particle1'"]
        self._caseSensitive=True
        self._exactMatch=True

class FindAlgorithmTestCase(unittest.TestCase):
    def printDebug(self,dialog):
        logging.debug(self.__class__.__name__ +': label: '+dialog.label()+', propert: '+str(dialog.properties())+', scripts: '+str(dialog.scripts())+', caseSensitive='+str(dialog.caseSensitive())+', exactMatch='+str(dialog.exactMatch()))
        
    def testExample(self):
        logging.debug(self.__class__.__name__ +': testExample()')
        dialog=TestFindDialog()
        findAlgoritm=FindAlgorithm()
        accessor=TestDataAccessor()
        findAlgoritm.setDataAccessor(accessor)
        findAlgoritm.setDataObjects(accessor.topLevelObjects())
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(len(findAlgoritm.results()),10)
        dialog.test1()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["container1"])
        dialog.test2()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["particle1"])
        dialog.test3()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(len(findAlgoritm.results()),10)
        dialog.test4()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(len(findAlgoritm.results()),7)
        self.assertEqual(findAlgoritm.next(),"particle2")
        self.assertEqual(findAlgoritm.previous(),"particle1")
        self.assertEqual(findAlgoritm.previous(),"particle7")
        self.assertEqual(findAlgoritm.next(),"particle1")
        dialog.test5()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["particle1"])
        dialog.test6()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),[])
        dialog.test7()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),[])
        dialog.test8()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["particle6"])
        dialog.test9()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["particle1"])
        dialog.test10()
        self.printDebug(dialog)
        findAlgoritm.findUsingFindDialog(dialog)
        self.assertEqual(findAlgoritm.results(),["particle1"])

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__,"FindAlgorithm")
