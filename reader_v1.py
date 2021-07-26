from PyQt5.QtCore import QObject, pyqtSignal
import serial
import time
from minimalmodbus import Instrument

class reader(QObject):
    data_signal = pyqtSignal(list)
    finished = pyqtSignal()
    
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.continue_logging = False
        self.data = []

    def start_recording(self):
        self.continue_logging = True

    def stop_recording(self):
        self.continue_logging = False


class arduino_reader(reader):
    def start_recording(self):
        super().start_recording()
        self.ser = serial.Serial(self.port)
        while self.continue_logging:
            val = self.ser.readline()
            timestamp = time.time()
            val = float(str(val).lstrip("b'")[:-5])
            self.ser.reset_output_buffer()
            self.data.append((timestamp, val))
            #print((timestamp, val))
        self.ser.close()
        self.data_signal.emit(self.data)
        self.finished.emit()


class modbus_reader(reader):
    def __init__(self, port, inlet_register, outlet_register, address):
        super().__init__(port)
        self.inlet_register = inlet_register
        self.outlet_register = outlet_register
        self.address = address

    def start_recording(self):
        super().start_recording()
        device = Instrument(self.port, self.address)
        while self.continue_logging:
            inlet_pressure = device.read_register(self.inlet_register)
            timestamp = time.time()
            outlet_pressure = device.read_register(self.outlet_register)
            self.data.append((timestamp, inlet_pressure, outlet_pressure))
        device.serial.close()
        self.data_signal.emit(self.data)
        self.finished.emit()
