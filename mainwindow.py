# This Python file uses the following encoding: utf-8
import sys
import pulsectl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtCore, QtWidgets

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pulse = pulsectl.Pulse('my-client-name')
        self.selected = ""
        list = self.list_procs()
        self.layout = QtWidgets.QGridLayout(self)

        self.dict = {}
        self.label = []
        #preciso buscar todos as sinks que tem application.name igual e agrupar
        for x in list:
          appname = x.proplist.get("application.name")

          if appname != None and appname not in self.dict:
                  self.dict[appname] = []
          if appname != None:
            self.dict[appname].append(x.index)

          if appname != None and appname not in self.label:
              self.label.append(appname)
              button = QtWidgets.QPushButton(" Sink Name: " + appname)
              button.clicked.connect(lambda checked=False, name=appname: self.magic(name))
              self.layout.addWidget(button)

        print(self.dict)
        button = QtWidgets.QPushButton("Unload virtual input")
        button.clicked.connect(self.unload)
        self.layout.addWidget(button)


    @QtCore.Slot()
    def magic(self, sink_index):
        proccesses = ""
        default_sink = self.pulse.sink_default_get()
        print(default_sink.name)
        self.pulse.module_load("module-null-sink", "sink_name=Virtual_Sink")
        self.pulse.module_load("module-combine-sink", f"slaves={default_sink.name},Virtual_Sink sink_name=Combined_Shared_Sink sink_properties=device.description=Combined_Process_Sink")

        sink_combined = self.pulse.get_sink_by_name("Combined_Shared_Sink")
        for x in self.dict[sink_index]:
            print("sink_id: " + str(x) + " added")
            proccesses += str(x) + ","
            self.pulse.sink_input_move(x, sink_combined.index)

        self.text = QtWidgets.QLabel(proccesses + " Added.")
        self.layout.addWidget(self.text)
        self.pulse.default_set(default_sink)

    def unload(self):
        sink = self.pulse.get_sink_by_name("Virtual_Sink")
        sink_combined = self.pulse.get_sink_by_name("Combined_Shared_Sink")
        self.pulse.module_unload(sink.owner_module)
        self.pulse.module_unload(sink_combined.owner_module)

    #lista processos
    def list_procs(self):        
        obj = self.pulse.sink_input_list()
        return obj

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
