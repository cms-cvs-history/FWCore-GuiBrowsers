import logging

from PyQt4.QtCore import Qt,QCoreApplication

from Vispa.Main.Application import Application
from Vispa.Views.BoxDecayView import BoxDecayView
from Vispa.Gui.PortConnection import PortConnection,PointToPointConnection

class ConfigEditorBoxView(BoxDecayView):
    """
    """
    
    LABEL="ConfigEditor BoxView"
    
    def __init__(self, parent=None,label=""):
        logging.debug(__name__ + ": __init__")
        BoxDecayView.__init__(self, parent)
        self._connections = []
        self._colors = [Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta]
        self._colorIndex = 0
        PointToPointConnection.CONNECTION_THICKNESS=3
        self.setSortBeforeArranging(False)

    def connections(self):
        return self._connections

    def setConnections(self, connections):
        """ Sets the connections between the objects.
        
        You need to call updateContent() in order to make the changes visible.
        """
        self._colorIndex = 0
        self._connections = connections
        
    def createConnections(self, operationId, widgetParent):
        for connection in self._connections:
            # Process application event loop in order to accept user input during time consuming drawing operation
            self._updateCounter+=1
            if self._updateCounter>=self.UPDATE_EVERY:
                self._updateCounter=0
                if not Application.NO_PROCESS_EVENTS:
                    QCoreApplication.instance().processEvents()
            # Abort drawing if operationId out of date
            if operationId != self._operationId:
                return None
            w1 = self.widgetByObject(connection[0])
            w2 = self.widgetByObject(connection[2])
            if w1 and w2:
                col = - 1
                if widgetParent:
                    for w in widgetParent.children():
                        if isinstance(w, PortConnection):
                            if w.sourcePort() == self.createSourcePort(w1, connection[1]):
                                col = w.colorIndex
                            if w.sinkPort().parent() == w1:
                                col = w.colorIndex
                if col < 0:
                    self._colorIndex += 1
                    if self._colorIndex >= len(self._colors):
                        self._colorIndex = 0
                    col = self._colorIndex
                connectionWidget = self.createConnection(w1, connection[1], w2, connection[3], self._colors[col])
                connectionWidget.colorIndex = self._colorIndex
                connectionWidget.show()
        return True

class ConnectionStructureView(ConfigEditorBoxView):
    LABEL="Connection structure"

class SequenceStructureView(ConfigEditorBoxView):
    LABEL="Sequence structure"

