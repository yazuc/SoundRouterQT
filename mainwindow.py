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
        dict = [""]

        for x in list:
          print(x.name)
          appname = x.proplist["application.name"]
          if not dict.__contains__(appname):
              dict.append(appname)
              button = QtWidgets.QPushButton(" Sink Name: " + appname)
              button.clicked.connect(lambda checked=False, name=x.index: self.magic(name))
              self.layout.addWidget(button)

        button = QtWidgets.QPushButton("Unload virtual input")
        button.clicked.connect(self.unload)
        self.layout.addWidget(button)


    @QtCore.Slot()
    def magic(self, sink_index):
        self.text = QtWidgets.QLabel(str(sink_index))
        self.layout.addWidget(self.text)
        default_sink = self.pulse.sink_default_get()
        print(default_sink.name)
        self.pulse.module_load("module-null-sink", "sink_name=Virtual_Sink")
        self.pulse.module_load("module-combine-sink", f"slaves={default_sink.name},Virtual_Sink sink_name=Combined_Shared_Sink sink_properties=device.description=Combined_Process_Sink")

        sink_combined = self.pulse.get_sink_by_name("Combined_Shared_Sink")

        self.pulse.sink_input_move(sink_index, sink_combined.index)
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
