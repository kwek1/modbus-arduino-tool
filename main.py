from reader import arduino_reader, modbus_reader
from dataprocesser import dataProcesser
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal
import sys
from serial.tools import list_ports
from datetime import datetime


class Ui(QtWidgets.QMainWindow):
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi("./assets/gui.ui", self)
        self.setFixedSize(666, 294)
        self.started = False

        self.ard_portrefresh.clicked.connect(
            lambda x: self.update_ports(self.arduino_port))
        self.mod_portrefresh.clicked.connect(
            lambda x: self.update_ports(self.modbus_port))

        self.startstop_button.clicked.connect(self.toggle_logging)

        self.filebrowse.clicked.connect(self.select_file_path)

    def update_data(self, source, data):
        # print(f"updating {source} data")
        self.collected_data[source] = data
        if len(self.collected_data) == 3:
            self.process_data()

    def update_ports(self, target):
        target.clear()
        ports = [i.device for i in list_ports.comports()]
        if ports:
            for i in ports:
                target.addItem(i)
            self.statusdisplay.append("ports refreshed")
        else:
            self.statusdisplay.append("no ports found")

    def select_file_path(self):
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select Folder')
        self.file_path_box.setText(folderpath)

    def toggle_logging(self):
        if self.started == False:  # start logging
            if not (self.modbus_port.currentText() and self.arduino_port.currentText):
                self.statusdisplay.append("select ports >:-(")
                return
            self.collected_data = {}
            self.collected_data['run_num'] = self.run_number.value()
            # set up thread for arduino
            self.arduino_thread = QThread()
            self.arduino = arduino_reader(self.arduino_port.currentText())
            self.stop_signal.connect(self.arduino.stop_recording)
            self.arduino.moveToThread(self.arduino_thread)

            # start/stop the thread
            self.arduino_thread.started.connect(self.arduino.start_recording)
            self.arduino_thread.finished.connect(self.arduino.stop_recording)

            # record the data before discarded
            self.arduino.data_signal.connect(
                lambda x: self.update_data("arduino", x))

            # garbage collection for arduino_reader object and arduino thread once finished
            self.arduino.finished.connect(self.arduino_thread.quit)
            self.arduino.finished.connect(self.arduino.deleteLater)
            self.arduino_thread.finished.connect(
                self.arduino_thread.deleteLater)

            # repeat above for modbus recording
            self.modbus_thread = QThread()
            self.modbus = modbus_reader(self.modbus_port.currentText(),
                                        self.inlet_register.value(),
                                        self.outlet_register.value(),
                                        self.slave_address.value())
            self.stop_signal.connect(self.modbus.stop_recording)
            self.modbus.moveToThread(self.modbus_thread)
            self.modbus_thread.started.connect(self.modbus.start_recording)
            self.modbus_thread.finished.connect(self.modbus.stop_recording)
            self.modbus.data_signal.connect(
                lambda x: self.update_data("modbus", x))
            self.modbus.finished.connect(self.modbus_thread.quit)
            self.modbus.finished.connect(self.modbus.deleteLater)
            self.modbus_thread.finished.connect(self.modbus_thread.deleteLater)

            # disable input fields and change button text
            self.arduinobox.setEnabled(False)
            self.modbusbox.setEnabled(False)

            self.file_path_box.setEnabled(False)
            self.filebrowse.setEnabled(False)
            self.label_6.setEnabled(False)
            self.label_7.setEnabled(False)
            self.run_number.setEnabled(False)
            self.startstop_button.setText("Stop")

            # start!!11!!!!!111
            self.statusdisplay.append(
                f"logging started at {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
            self.arduino_thread.start()
            self.modbus_thread.start()
            self.started = True
        else:
            self.stop_signal.emit()
            self.statusdisplay.append(
                f"logging stopped at {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
            self.arduinobox.setEnabled(True)
            self.modbusbox.setEnabled(True)
            self.file_path_box.setEnabled(True)
            self.filebrowse.setEnabled(True)
            self.label_6.setEnabled(True)
            self.label_7.setEnabled(True)
            self.run_number.setEnabled(True)
            self.startstop_button.setText("Start")
            self.started = False
            self.statusdisplay.append('collating data...')
            self.run_number.setValue(self.run_number.value() + 1)

    def process_data(self):
        # data processing is shifted to another thread to prevent unresponsiveness
        # (although doesnt really take long)
        # print(self.collected_data)
        self.processor = dataProcesser(
            self.collected_data, self.file_path_box.text())
        self.data_pro_thread = QThread()
        self.processor.moveToThread(self.data_pro_thread)
        self.data_pro_thread.started.connect(self.processor.run)
        self.processor.finished.connect(self.data_pro_thread.quit)
        self.processor.finished.connect(self.processor.deleteLater)
        self.processor.progress.connect(lambda x: self.statusdisplay.append(x))
        self.data_pro_thread.finished.connect(self.data_pro_thread.deleteLater)
        self.statusdisplay.append('processing data...')
        self.data_pro_thread.start()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
sys.exit(app.exec_())
