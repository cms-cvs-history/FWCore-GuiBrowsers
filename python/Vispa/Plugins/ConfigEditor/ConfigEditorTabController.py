import sys
import logging
import os.path
import copy

from PyQt4.QtCore import SIGNAL,QString,QCoreApplication
from PyQt4.QtGui import QMessageBox,QFileDialog

from Vispa.Main.Application import Application
from Vispa.Main.Exceptions import exception_traceback
from Vispa.Share.ThreadChain import ThreadChain
from Vispa.Plugins.Browser.BrowserTabController import BrowserTabController
from Vispa.Views.WidgetView import WidgetView
from Vispa.Plugins.ConfigEditor.ConfigEditorBoxView import ConfigEditorBoxView,ConnectionStructureView,SequenceStructureView

try:
    from FWCore.GuiBrowsers.DOTExport import DotExport
    import_dotexport_error=None
except Exception,e:
    import_dotexport_error=(str(e),exception_traceback())

try:
    from ToolDataAccessor import ToolDataAccessor,ConfigToolBase,standardConfigDir
    from ToolDialog import ToolDialog
    import_tools_error=None
except Exception,e:
    import_tools_error=(str(e),exception_traceback())

class ConfigEditorTabController(BrowserTabController):
    """
    """
    def __init__(self, plugin):
        logging.debug(__name__ + ": __init__")
        BrowserTabController.__init__(self, plugin)

        self._editorName = ""
        self._thread = None
        self._originalSizes=[100,1,200]
        self._toolDialog=None
        
        self._configMenu = self.plugin().application().createPluginMenu('&Config')
        self._configToolBar = self.plugin().application().createPluginToolBar('&Config')
        openEditorAction = self.plugin().application().createAction('&Open in custom editor', self.openEditor, "F6")
        self._configMenu.addAction(openEditorAction)
        chooseEditorAction = self.plugin().application().createAction('&Choose custom editor...', self.chooseEditor, "Ctrl+T")
        self._configMenu.addAction(chooseEditorAction)
        self._configMenu.addSeparator()
        self._dumpAction = self.plugin().application().createAction('&Dump python config to single file...', self.dumpPython, "Ctrl+D")
        self._configMenu.addAction(self._dumpAction)
        self._dotExportAction = self.plugin().application().createAction('&Export dot graphic...', self.exportDot, "Ctrl+G")
        self._configMenu.addAction(self._dotExportAction)
        self._configMenu.addSeparator()
        self._editorAction = self.plugin().application().createAction('&Start ConfigEditor', self.startEditMode, "F8")
        self._configMenu.addAction(self._editorAction)
        self._configToolBar.addAction(self._editorAction)
        
    #@staticmethod
    def staticSupportedFileTypes():
        """ Returns supported file type: py.
        """
        return [('py', 'Config file')]
    staticSupportedFileTypes = staticmethod(staticSupportedFileTypes)
    
    def dotExportAction(self):
        return self._dotExportAction
    
    def dumpAction(self):
        return self._dumpAction
    
    def updateCenterView(self, propertyView=True):
        """ Fill the center view from an item in the TreeView and update it """
        statusMessage = self.plugin().application().startWorking("Updating center view")
        if propertyView:
            self.selectDataAccessor(True)
        else:
            self.selectDataAccessor(self.tab().propertyView().dataObject())
        if self._thread != None and self._thread.isRunning():
            self.dataAccessor().cancelOperations()
            while self._thread.isRunning():
                if not Application.NO_PROCESS_EVENTS:
                    QCoreApplication.instance().processEvents()
        objects = []
        select=self.tab().treeView().selection()
        if select != None:
            if self.currentCenterViewClassId() == self.plugin().viewClassId(ConnectionStructureView):
                objects = self.dataAccessor().nonSequenceChildren(select)
            else:
                objects = [select]
        self.tab().centerView().setDataObjects(objects)
        if self.currentCenterViewClassId() == self.plugin().viewClassId(ConnectionStructureView):
            self._thread = ThreadChain(self.dataAccessor().readConnections, objects)
            while self._thread.isRunning():
                if not Application.NO_PROCESS_EVENTS:
                    QCoreApplication.instance().processEvents()
            if self._thread.returnValue():
                if isinstance(self.tab().centerView(), ConfigEditorBoxView):
                    self.tab().centerView().setArrangeUsingRelations(True)
                    self.tab().centerView().setConnections(self.dataAccessor().connections())
        else:
            if isinstance(self.tab().centerView(), ConfigEditorBoxView):
                self.tab().centerView().setArrangeUsingRelations(False)
                self.tab().centerView().setConnections([])
        if self.tab().centerView().updateContent():
            self.tab().centerView().restoreSelection()
            select = self.tab().centerView().selection()
            if select != None:
                if self.tab().propertyView().dataObject() != select and propertyView:
                    self.tab().propertyView().setDataObject(select)
                    self.tab().propertyView().updateContent()
        self.plugin().application().stopWorking(statusMessage)
        
    def selected(self):
        """ Shows plugin menus when user selects tab.
        """
        logging.debug(__name__ + ": selected()")
        BrowserTabController.selected(self)
        self.plugin().application().showPluginMenu(self._configMenu)
        self.plugin().application().showPluginToolBar(self._configToolBar)
        self._editorAction.setVisible(not self.tab().editorSplitter())
        if self.tab().editorSplitter():
            self._applyPatToolAction.setVisible(self.dataAccessor().process()!=None)
        self.tab().mainWindow().application().showZoomToolBar()

    def openEditor(self):
        """ Call editor """
        logging.debug(__name__ + ": openEditor")
        selected_object = self.tab().propertyView().dataObject()
        filename = self.dataAccessor().fullFilename(selected_object)
        if self._editorName != "" and selected_object != None and os.path.exists(filename):
            if os.path.expandvars("$CMSSW_RELEASE_BASE") in filename:
                QMessageBox.information(self.tab(), "Opening readonly file...", "This file is from $CMSSW_RELEASE_BASE and readonly") 
            command = self._editorName
            command += " " + filename
            command += " &"
            os.system(command)

    def chooseEditor(self, _editorName=""):
        """ Choose editor using FileDialog """
        logging.debug(__name__ + ": chooseEditor")
        if _editorName == "":
            _editorName = str(QFileDialog.getSaveFileName(self.tab(), "Choose editor", self._editorName, "Editor (*)", None , QFileDialog.DontConfirmOverwrite or QFileDialog.DontResolveSymlinks))
            if not os.path.exists(_editorName):
                _editorName = os.path.basename(_editorName)
        if _editorName != None and _editorName != "":
            self._editorName = _editorName
        self.saveIni()

    def dumpPython(self, fileName=None):
        """ Dump python configuration to file """
        logging.debug(__name__ + ": dumpPython")
        dump = self.dataAccessor().dumpPython()
        if dump == "":
            logging.error(self.__class__.__name__ +": dumpPython() - "+"Cannot dump this config because it does not 'process'.\nNote that only 'cfg' files contain a 'process'.)")
            self.plugin().application().errorMessage("Cannot dump this config because it does not 'process'.\nNote that only 'cfg' files contain a 'process'.)")
            return None
        filter = QString("")
        if not fileName:
            defaultname = os.path.splitext(self._filename)[0] + "_dump" + os.path.splitext(self._filename)[1]
            fileName = str(QFileDialog.getSaveFileName(self.tab(), "Save python config...", defaultname, "Python config (*.py)", filter))
        if fileName != "":
            name = fileName
            ext = "PY"
            if os.path.splitext(fileName)[1].upper().strip(".") == ext:
                name = os.path.splitext(fileName)[0]
                ext = os.path.splitext(fileName)[1].upper().strip(".")
            text_file = open(name + "." + ext.lower(), "w")
            text_file.write(dump)
            text_file.close()

    def loadIni(self):
        """ read options from ini """
        ini = self.plugin().application().ini()
        if ini.has_option("config", "editor"):
            self._editorName = str(ini.get("config", "editor"))
        else:
            self._editorName = "emacs"
        if ini.has_option("config", "CurrentView"):
            proposed_view = ini.get("config", "CurrentView")
        else:
            proposed_view = self.plugin().viewClassId(ConnectionStructureView)
        self.switchCenterView(proposed_view)
        if ini.has_option("config", "box content script") and isinstance(self.centerView(),ConfigEditorBoxView):
            self.centerView().setBoxContentScript(str(ini.get("config", "box content script")))
            self._boxContentDialog.setScript(str(ini.get("config", "box content script")))

    def scriptChanged(self, script):
        BrowserTabController.scriptChanged(self, script)
        self.saveIni()

    def saveIni(self):
        """ write options to ini """
        ini = self.plugin().application().ini()
        if not ini.has_section("config"):
            ini.add_section("config")
        ini.set("config", "editor", self._editorName)
        if self.currentCenterViewClassId():
            ini.set("config", "CurrentView", self.currentCenterViewClassId())
        if isinstance(self.centerView(),ConfigEditorBoxView):
            ini.set("config", "box content script", self.centerView().boxContentScript())
        self.plugin().application().writeIni()

    def exportDot(self, fileName=None):
        if import_dotexport_error!=None:
            logging.error(__name__ + ": Could not import DOTExport: "+import_dotexport_error[1])
            self.plugin().application().errorMessage("Could not import DOTExport (see logfile for details):\n"+import_dotexport_error[0])
            return
        dot = DotExport()
        if self.currentCenterViewClassId() == self.plugin().viewClassId(ConnectionStructureView):
            presets = {'endpath':False, 'source':False, 'legend':False}
        else:
            presets = {'seqconnect':True, 'tagconnect':False, 'legend':False}
        for opt, val in presets.items():
            dot.setOption(opt, val)
        types = ""
        for ft in dot.file_types:
            if types != "":
                types += ";;"
            types += ft.upper() + " File (*." + ft.lower() + ")"
        filter = QString("PDF File (*.pdf)")
        if not fileName:
            defaultname = os.path.splitext(self._filename)[0] + "_export"
            fileName = str(QFileDialog.getSaveFileName(self.tab(), "Export dot graphic...", defaultname, types, filter))
        if fileName != "":
            name = fileName
            ext = str(filter).split(" ")[0].lower()
            if os.path.splitext(fileName)[1].lower().strip(".") in dot.file_types:
                name = os.path.splitext(fileName)[0]
                ext = os.path.splitext(fileName)[1].lower().strip(".")
            try:
                dot.export(self.dataAccessor(), name + "." + ext, ext)
            except Exception:
                try:
                    dot.export(self.dataAccessor(), name + ".dot", "dot")
                    logging.error(self.__class__.__name__ +": exportDot() - "+"'dot' executable not found which is needed for conversion to '*." + ext + "'. Created '*.dot' file instead.")
                    self.plugin().application().errorMessage("'dot' executable not found which is needed for conversion to '*." + ext + "'. Created '*.dot' file instead.")
                except Exception,e:
                    logging.error(self.__class__.__name__ +": exportDot() - "+"Could not export dot graphic (see logfile for details): " + str(e))
                    self.plugin().application().errorMessage("Could not export dot graphic: " + exception_traceback())

    def readFile(self, filename):
        """ Reads in the file in a separate thread.
        """
        thread = ThreadChain(self.dataAccessor().open, filename)
        while thread.isRunning():
            if not Application.NO_PROCESS_EVENTS:
                QCoreApplication.instance().processEvents()
        if thread.returnValue():
            if not self.dataAccessor().process() and self.dumpAction().isEnabled()==True:
                self.dumpAction().setEnabled(False)
            if self.plugin().application().commandLineOptions().saveimage:
                self.tab().centerView().updateConnections()
                self.saveImage(self.plugin().application().commandLineOptions().saveimage)
                print "Saved image to", self.plugin().application().commandLineOptions().saveimage, "."
                sys.exit(2)
            return True
        return False

    def save(self, filename=''):
        logging.debug(__name__ + ': save')
        self.startEditMode()
        if filename != "":
            if os.path.basename(filename) == os.path.basename(self.dataAccessor().configFile()):
                logging.error(self.__class__.__name__ +": save() - "+"Cannot use name of original configuration file: "+str(filename))
                self.plugin().application().errorMessage("Cannot use name of original configuration file.")
            elif BrowserTabController.save(self, filename):
                self.dataAccessor().setIsReplaceConfig()
                return True
            else:
                return False
        elif self.dataAccessor().isReplaceConfig():
            return BrowserTabController.save(self, filename)
        return self.tab().mainWindow().application().saveFileAsDialog()

    def writeFile(self, filename):
        """ Write replace config file.
        """
        logging.debug(__name__ + ': writeFile')
        
        text_file = open(filename, "w")
        text_file.write(self.toolDataAccessor().topLevelObjects()[0].dumpPython()[1])
        text_file.write(self.dataAccessor().process().dumpHistory(False))
        text_file.close()
        return True

    def open(self, filename=None, update=True):
        if BrowserTabController.open(self, filename, update):
            if self.dataAccessor().isReplaceConfig():
                self.startEditMode()
            return True
        return False

    def startEditMode(self):
        if import_tools_error!=None:
            logging.error(__name__ + ": Could not import tools for ConfigEditor: "+import_tools_error[1])
            self.plugin().application().errorMessage("Could not import tools for ConfigEditor (see logfile for details):\n"+import_tools_error[0])
            return
        if self.tab().editorSplitter():
            return
        if self._filename and not self.dataAccessor().process():
            logging.error(__name__ + ": Config does not contain a process and cannot be edited using ConfigEditor.")
            self.plugin().application().errorMessage("Config does not contain a process and cannot be edited using ConfigEditor.")
            return
        if self._filename and not self.dataAccessor().isReplaceConfig():
            self.setFilename(None)
            self.updateLabel()
        self.tab().createEditor()
        self.tab().verticalSplitter().setSizes(self._originalSizes)

        self._importAction = self.plugin().application().createAction('&Import configuration...', self.importButtonClicked, "F2")
        self._configMenu.addAction(self._importAction)
        self._configToolBar.addAction(self._importAction)
        self._applyPatToolAction = self.plugin().application().createAction('&Apply PAT tool...', self.applyButtonClicked, "F3")
        self._configMenu.addAction(self._applyPatToolAction)
        self._configToolBar.addAction(self._applyPatToolAction)
        self.selected()

        self._toolDataAccessor=ToolDataAccessor()
        self._toolDataAccessor.setConfigDataAccessor(self.dataAccessor())
        self.tab().editorTableView().setDataAccessor(self._toolDataAccessor)
        self.connect(self.tab().editorTableView(), SIGNAL('importButtonClicked'), self.importButtonClicked)
        self.connect(self.tab().editorTableView(), SIGNAL('applyButtonClicked'), self.applyButtonClicked)
        self.connect(self.tab().editorTableView(), SIGNAL('removeButtonClicked'), self.removeButtonClicked)
        self.connect(self.tab().editorTableView(), SIGNAL('selected'), self.codeSelected)
        self.connect(self.tab().propertyView(), SIGNAL('valueChanged'), self._updateCode)
        self._updateCode()

    def toolDataAccessor(self):
        return self._toolDataAccessor

    def minimizeEditor(self):
        if self.tab().originalButton().isChecked():
            self._originalSizes=self.tab().verticalSplitter().sizes()
        self.tab().minimizeButton().setChecked(True)
        self.tab().originalButton().setChecked(False)
        self.tab().maximizeButton().setChecked(False)
        self.tab().verticalSplitter().setSizes([100, 1, 0])
    
    def originalEditor(self):
        self.tab().minimizeButton().setChecked(False)
        self.tab().originalButton().setChecked(True)
        self.tab().maximizeButton().setChecked(False)
        self.tab().verticalSplitter().setSizes(self._originalSizes)

    def maximizeEditor(self):
        if self.tab().originalButton().isChecked():
            self._originalSizes=self.tab().verticalSplitter().sizes()
        self.tab().minimizeButton().setChecked(False)
        self.tab().originalButton().setChecked(False)
        self.tab().maximizeButton().setChecked(True)
        self.tab().verticalSplitter().setSizes([0, 1, 100])
    
    def _updateCode(self):
        logging.debug(__name__ + ": _updateCode")
        self.toolDataAccessor().updateToolList()
        self.tab().editorTableView().setDataObjects(self.toolDataAccessor().topLevelObjects())
        if self.tab().editorTableView().updateContent():
            self.tab().editorTableView().restoreSelection()

    def importConfig(self,filename):
        statusMessage = self.plugin().application().startWorking("Import python configuration in Editor")
        try:
            good=self.open(filename,False)
        except:
            logging.error(__name__ + ": Could not open configuration file: "+exception_traceback())
            self.plugin().application().errorMessage("Could not open configuration file (see log file for details).")
            return False
        if not good:
            logging.error(__name__ + ": Could not open configuration file.")
            self.plugin().application().errorMessage("Could not open configuration file.")
            return False
        if not self.dataAccessor().process():
            logging.error(__name__ + ": Config does not contain a process and cannot be edited using ConfigEditor.")
            self.plugin().application().errorMessage("Config does not contain a process and cannot be edited using ConfigEditor.")
            return False
        if self._filename and not self.dataAccessor().isReplaceConfig():
            self.setFilename(None)
            self.updateLabel()
        self.toolDataAccessor().setConfigDataAccessor(self.dataAccessor())
        self._updateCode()
        self.plugin().application().stopWorking(statusMessage)
        self.tab().propertyView().setDataObject(None)
        self.updateContent()
        return True

    def setModified(self, modified=True, update=True):
        logging.debug(__name__ + ": setModified")
        BrowserTabController.setModified(self, modified)
        if not update:
            return True
        if isinstance(self.tab().propertyView().dataObject(),ConfigToolBase):
            if self._toolDataAccessor.label(self.tab().propertyView().dataObject())=="Import":
                filename=self.toolDataAccessor().propertyValue(self.tab().propertyView().dataObject(),"filename")
                return self.importConfig(filename)
            else:
                self.toolDataAccessor().updateProcess()
                self._updateCode()
                self.tab().editorTableView().select(self.tab().editorTableView().dataObjects()[-1])
        return True

    def updateConfigContent(self):
        if self.tab().editorTableView().selection() in self.toolDataAccessor().toolModules().keys():
            self._filterObjects=self.toolDataAccessor().toolModules()[self.tab().editorTableView().selection()]
        elif self._filterObjects!=None:
            self._filterObjects=None
        self.updateContent(False,False)
            
    def importButtonClicked(self):
        logging.debug(__name__ + ": importButtonClicked")
        filename = QFileDialog.getOpenFileName(
            self.tab(),'Select a configuration file',standardConfigDir,"Python configuration (*.py)")
        if not filename.isEmpty():
            self.importConfig(str(filename))

    def applyButtonClicked(self):
        logging.debug(__name__ + ": applyButtonClicked")
        if not self._toolDialog:
            self._toolDialog=ToolDialog()
            self._toolDialog.setDataAccessor(self._toolDataAccessor)
        if not self._toolDialog.exec_():
            return
        if not self.toolDataAccessor().addTool(self._toolDialog.tool()):
            return
        self.setModified(True,False)
        self._updateCode()
        self.tab().editorTableView().select(self.tab().editorTableView().dataObjects()[-2])
        self.codeSelected(self.tab().editorTableView().dataObjects()[-1])
            
    def removeButtonClicked(self,object):
        logging.debug(__name__ + ": removeButtonClicked")
        if not object or not self.dataAccessor().process() or\
            self._toolDataAccessor.label(object) in ["Import","ApplyTool"]:
            return
        if not self.toolDataAccessor().removeTool(object):
            self.plugin().application().errorMessage("Could not apply tool. See log file for details.")
            return
        self.setModified(True,False)
        self._updateCode()
        self.tab().editorTableView().select(self.tab().editorTableView().dataObjects()[-1])
        self.codeSelected(self.tab().editorTableView().dataObjects()[-1])

    def onSelected(self, select):
        self.selectDataAccessor(select)
        BrowserTabController.onSelected(self, select)

    def updateContent(self, filtered=False, propertyView=True):
        self.selectDataAccessor(self.tab().propertyView().dataObject())
        BrowserTabController.updateContent(self, filtered, propertyView)

    def select(self, object):
        self.selectDataAccessor(object)
        BrowserTabController.select(self, object)
    
    def selectDataAccessor(self,object):
        if import_tools_error==None and isinstance(object,ConfigToolBase):
            self.tab().propertyView().setDataAccessor(self.toolDataAccessor())
        else:
            self.tab().propertyView().setDataAccessor(self.dataAccessor())
    
    def codeSelected(self,select):
        if self.tab().propertyView().dataObject() != select:
            statusMessage = self.plugin().application().startWorking("Updating property view")
            self.tab().propertyView().setDataAccessor(self.toolDataAccessor())
            self.tab().propertyView().setDataObject(select)
            self.tab().propertyView().updateContent()
            self.plugin().application().stopWorking(statusMessage)
        self.updateConfigContent()
