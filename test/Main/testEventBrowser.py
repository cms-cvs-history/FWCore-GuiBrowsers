#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *

from Vispa.Main.Application import *
from Vispa.Main.VispaPlugin import *
from Vispa.Main.EventBrowserTab import *
from Vispa.Main.EventBrowserTabController import *
from TestDataAccessor import *
from Vispa.Main import Profiling

class EventBrowserTestCase(unittest.TestCase):
    def testEventBrowser(self):
        logging.debug(self.__class__.__name__ +': testRun()')
        self.app=Application(sys.argv)
        self.app.mainWindow().setWindowTitle("test EventBrowser")
        self.plugin=VispaPlugin(self.app)
        self.controller = EventBrowserTabController(self.plugin)
        self.tab = EventBrowserTab(self.app.mainWindow())
        self.tab.setController(self.controller)
        self.app.mainWindow().addTab(self.tab)
        self.controller.setDataAccessor(TestDataAccessor())
        self.app.run()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__)
