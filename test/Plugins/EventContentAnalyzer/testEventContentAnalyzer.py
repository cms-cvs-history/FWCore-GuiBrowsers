#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *
examplesDirectory1 = os.path.join(baseDirectory,"examples/Plugins/ConfigBrowser")
examplesDirectory2 = os.path.join(baseDirectory,"examples/Plugins/EdmBrowser")
examplesDirectory3 = os.path.join(baseDirectory,"examples/Plugins/EventContentAnalyzer")

from Vispa.Main.Application import *
from Vispa.Plugins.EventContentAnalyzer.EventContentAnalyzerPlugin import *
from Vispa.Main import Profiling

class EventContentAnalyzerTestCase(unittest.TestCase):
    def testEventContentAnalyzer(self):
        logging.debug(self.__class__.__name__ +': testRun()')
        self.app=Application(sys.argv)
        self.app.mainWindow().setWindowTitle("test EventContentAnalyzer")
        for plugin in self.app.plugins():
            if plugin.__class__.__name__==EventContentAnalyzerPlugin.__name__:
                tab, controller=plugin.newTab()
#        controller.addRootFile(os.path.join(examplesDirectory2,"RelValTTbar_CMSSW_2_1_7_IDEAL_V9_v2_GEN-SIM-RECO_aod_10events.root"))
        controller.addTextFile(os.path.join(examplesDirectory3,"aod.txt"))
#        controller.addConfigFile(os.path.join(examplesDirectory1,"patLayer0_fromAOD_full_cfg_CMSSW_2_1_X.py"))
#        controller.addConfigFile(os.path.join(examplesDirectory1,"patLayer1_fromLayer0_full_cfg_CMSSW_2_1_X.py"))
        controller.addTextFile(os.path.join(examplesDirectory3,"pat.txt"))
        self.app.run()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__)
