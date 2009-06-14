#! /usr/bin/env python
import unittest
import os.path
import sys

import logging
logging.root.setLevel(logging.DEBUG)

import Path
from Vispa.Main.Directories import *

from Vispa.Main.ZoomableScrollArea import *
from Vispa.Main.VispaWidget import *
from Vispa.Main.ZoomableWidget import *
from TestDataAccessor import *
from Vispa.Main import Profiling

class ZoomableWidgetTestCase(unittest.TestCase):
    def testExample(self):
        logging.debug(self.__class__.__name__ + ': testExample()')
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("test ZoomableWidget")
        self.window.resize(300,300)
        self.app.setActiveWindow(self.window)
        self.window.show()
        self.scrollArea = ZoomableScrollArea(self.window)
        self.window.setCentralWidget(self.scrollArea)
        self.zoomableWidget = ZoomableWidget()
        self.scrollArea.setWidget(self.zoomableWidget)
        self.widget=VispaWidget(self.zoomableWidget)
        self.widget.move(10,10)
        self.widget.show()
        self.zoomableWidget.exportImage()
        self.app.exec_()

if __name__ == "__main__":
    Profiling.analyze("unittest.main()",__file__,"ZoomableScrollArea|VispaWidget|ZoomableWidget")
