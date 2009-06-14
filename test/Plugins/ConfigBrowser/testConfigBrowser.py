#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *
examplesDirectory = os.path.join(baseDirectory,"examples/Plugins/ConfigBrowser")
test=1
if not os.path.exists(examplesDirectory):
    examplesDirectory = os.path.abspath(os.path.join(os.path.join(baseDirectory,".."),"examples"))
    test=2

from Vispa.Main.Application import *
from Vispa.Main import Profiling

class ConfigBrowserTestCase(unittest.TestCase):
    def testConfigBrowser(self):
        global test
        logging.debug(self.__class__.__name__ +': testRun()')
        self.app=Application(sys.argv)
        self.app.mainWindow().setWindowTitle("test ConfigBrowser")
        if test==1:
            self.app.openFile(os.path.join(examplesDirectory,"patLayer1_fromLayer0_full_cfg_CMSSW_2_1_X.py"))
        if test==2:
            self.app.openFile(os.path.join(examplesDirectory,"patLayer1_fromAOD_full_cfg_CMSSW_3_1_X.py"))
        self.app.run()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__)
