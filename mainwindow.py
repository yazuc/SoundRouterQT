# This Python file uses the following encoding: utf-8
import sys
import pulsectl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtCore, QtWidgets

#TODO: perguntar se quer unload() ao fechar
from ui_form import Ui_MainWindow

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QGridLayout(self)
        self.SetupDefault()


    def SetupDefault(self):
            self.pulse = pulsectl.Pulse('my-client-name')
            self.selected = ""
            list = self.list_procs()

            self.dict = {}
            self.label = []
            content = QtWidgets.QGridLayout()
            content.addWidget

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
                  content.addWidget(button)

            button = QtWidgets.QPushButton("Unload virtual input")
            button.clicked.connect(self.unload)

            reloadButton = QtWidgets.QPushButton("Refresh processes")
            reloadButton.clicked.connect(self.reload)

            layout_button = QtWidgets.QHBoxLayout()
            layout_button.addWidget(reloadButton)
            layout_button.addWidget(button)

            main_widget = QtWidgets.QWidget()
            main_widget.setLayout(content)
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setFixedHeight(300)
            self.scroll.setWidgetResizable(True)
            self.layout.addWidget(main_widget, 0, 0)
            self.layout.addWidget(self.scroll, 1, 0)
            self.layout.addLayout(layout_button, 2, 0)

    @QtCore.Slot()
    def magic(self, sink_index):
        proccesses = ""
        default_sink = self.pulse.sink_default_get()
        print(default_sink.name)
        self.pulse.module_load("module-null-sink", f"sink_name=Virtual_Sink sink_properties=device.description={sink_index}_virtualized" )
        self.pulse.module_load("module-combine-sink", f"slaves={default_sink.name},Virtual_Sink sink_name=Combined_Shared_Sink sink_properties=device.description=Combined_Process_Sink")

        sink_combined = self.pulse.get_sink_by_name("Combined_Shared_Sink")
        for x in self.dict[sink_index]:
            print("sink_id: " + str(x) + " added")
            proccesses += str(x) + ","
            self.pulse.sink_input_move(x, sink_combined.index)

        self.text = QtWidgets.QLabel(proccesses + f" Added into {sink_index}_virtualized")
        self.scroll.setWidget(self.text)
        self.pulse.default_set(default_sink)

    def unload(self):
        virtual_exists = True
        while virtual_exists:
                try:
                        sink = self.pulse.get_sink_by_name("Virtual_Sink")
                        sink_combined = self.pulse.get_sink_by_name("Combined_Shared_Sink")
                except Exception:
                        virtual_exists = False
                        sink = None
                        sink_combined = None
                        break

                if sink is not None and sink_combined is not None:
                        self.pulse.module_unload(sink.owner_module)
                        self.pulse.module_unload(sink_combined.owner_module)
                        self.text = QtWidgets.QLabel("Virtual sinks removed.")
                        self.scroll.setWidget(self.text)
                else:
                        self.text = QtWidgets.QLabel("No virtual sink to remove.")
                        self.scroll.setWidget(self.text)

    def reload(self):
        while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        self.SetupDefault()
        self.text = QtWidgets.QLabel("Processes refreshed.")
        self.scroll.setWidget(self.text)


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
    widget.setStyleSheet("QLabel {background-color: #FFFFFF;qproperty-alignment: AlignCenter;}QPushButton { background-color: #2ABf9E;padding: 20px;font-size: 18px;}")
    widget.show()
    sys.exit(app.exec())
