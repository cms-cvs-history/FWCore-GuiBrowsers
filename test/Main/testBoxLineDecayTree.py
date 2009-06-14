#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *

from Vispa.Main.ZoomableScrollArea import *
from Vispa.Main.BoxDecayTree import *
from Vispa.Main.LineDecayTree import *
from TestDataAccessor import *
from Vispa.Main import Profiling

class BoxDecayTreeTestCase(unittest.TestCase):
    def testExample(self):
        logging.debug(self.__class__.__name__ + ': testExample()')
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("test BoxDecayTree")
        self.window.resize(300,300)
        self.app.setActiveWindow(self.window)
        self.window.show()
        self.scrollArea = ZoomableScrollArea(self.window)
        self.window.setCentralWidget(self.scrollArea)
        self.boxDecayTree = BoxDecayTree()
        self.scrollArea.setWidget(self.boxDecayTree)
        accessor=TestDataAccessor()
        self.boxDecayTree.setDataAccessor(accessor)
        self.boxDecayTree.setDataObjects(accessor.topLevelObjects())
        self.boxDecayTree.setBoxContentScript("str(object.Label)")
        self.boxDecayTree.setSubView(LineDecayTree)
        self.boxDecayTree.updateContent()
        self.app.exec_()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__,"BoxDecayTree|LineDecayTree")
