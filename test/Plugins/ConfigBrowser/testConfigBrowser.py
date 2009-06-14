#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *
examplesDirectory = os.path.abspath(os.path.join(os.path.join(baseDirectory,".."),"examples"))

from Vispa.Main.Application import *
from Vispa.Main import Profiling

class ConfigBrowserTestCase(unittest.TestCase):
    def testConfigBrowser(self):
        logging.debug(self.__class__.__name__ +': testRun()')
        self.app=Application(sys.argv)
        self.app.mainWindow().setWindowTitle("test ConfigBrowser")
        self.app.openFile(os.path.join(examplesDirectory,"patLayer1_fromAOD_full_cfg_CMSSW_3_1_X.py"))
        self.app.run()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__)
