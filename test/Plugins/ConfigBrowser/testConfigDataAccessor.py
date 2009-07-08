#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *
sys.path.append(os.path.join(baseDirectory,"Vispa/Plugins/ConfigBrowser"))
examplesDirectory = os.path.join(baseDirectory,"examples/ConfigBrowser")
test=1
if not os.path.exists(examplesDirectory):
    examplesDirectory = os.path.abspath(os.path.join(os.path.join(baseDirectory,".."),"examples"))
    test=2

from Vispa.Main.Exceptions import *
try:
    from ConfigDataAccessor import *
except Exception:
    logging.error("Cannot open ConfigDataAccessor: " + exception_traceback())
from Vispa.Main import Profiling

class ConfigDataAccessorTestCase(unittest.TestCase):
    def testExample(self):
        global test
        logging.debug(self.__class__.__name__ +': testExample()')

        accessor=ConfigDataAccessor()
        if test==1:
            accessor.open(os.path.join(examplesDirectory,"patLayer1_cff_CMSSW_2_1_X.py"))

            self.assertEqual(len(accessor.topLevelObjects()),2)
            self.assertEqual(len(accessor.properties(accessor.topLevelObjects()[0])),8)
            self.assertEqual(len(accessor.children(accessor.topLevelObjects()[0])),8)
            self.assertEqual(accessor.label(accessor.topLevelObjects()[0]),"allObjects")

            accessor.open(os.path.join(examplesDirectory,"patLayer1_fromLayer0_full_cfg_CMSSW_2_1_X.py"))

            self.assertEqual(len(accessor.children(accessor.topLevelObjects()[0])),9)
            self.assertEqual(len(accessor.properties(accessor.children(accessor.topLevelObjects()[0])[0])),5)
            self.assertEqual(len(accessor.children(accessor.children(accessor.topLevelObjects()[0])[0])),1)
            self.assertEqual(accessor.label(accessor.children(accessor.topLevelObjects()[0])[0]),"source")
            
        if test==2:
            accessor.open(os.path.join(examplesDirectory,"cleanLayer1Objects_cff_CMSSW_3_1_X.py"))

            self.assertEqual(len(accessor.topLevelObjects()),2)
            self.assertEqual(len(accessor.properties(accessor.topLevelObjects()[0])),7)
            self.assertEqual(len(accessor.children(accessor.topLevelObjects()[0])),7)
            self.assertEqual(accessor.label(accessor.topLevelObjects()[0]),"cleanLayer1Objects")

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__)
