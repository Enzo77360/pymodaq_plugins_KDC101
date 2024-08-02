from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun, main)
import clr
import sys
import time
from System import Decimal, UInt32, Int32

# Ajouter le chemin d'accès aux DLLs Kinesis
kinesis_path = 'C:\\Program Files\\Thorlabs\\Kinesis'
sys.path.append(kinesis_path)

clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.DCServoCLI")

import Thorlabs.MotionControl.KCube.DCServoCLI as DCServo
import Thorlabs.MotionControl.DeviceManagerCLI as Device
import Thorlabs.MotionControl.GenericMotorCLI as Generic

# Construire la liste des périphériques disponibles
print("Building device list...")
Device.DeviceManagerCLI.BuildDeviceList()

# Préfixe correct pour les périphériques KCube DCServo
device_prefix = DCServo.KCubeDCServo.DevicePrefix
print(f"Device prefix: {device_prefix}")

# Obtenez la liste des périphériques en utilisant le préfixe approprié
device_list = Device.DeviceManagerCLI.GetDeviceList(device_prefix)
print(f"Device list: {device_list}")

# Sélectionnez seulement le premier périphérique si disponible
serialnumbers_Kcube = [str(device_list[0])] if device_list else []
print(f"Available serial numbers: {serialnumbers_Kcube}")

class Kinesis:
    def __init__(self):
        self._device = None

    def connect(self, serial: str):
        self._device.Connect(serial)
        self._device.WaitForSettingsInitialized(5000)
        self._device.StartPolling(250)
        print("Connected to device with serial:", serial)
        self._device.LoadMotorConfiguration(serial)
        self._device.EnableDevice()

    def close(self):
        """
            close the current instance of Kinesis instrument.
        """
        if self._device:
            self._device.StopPolling()
            self._device.Disconnect()
            self._device.Dispose()
            self._device = None
            print("Device closed")

    @property
    def name(self) -> str:
        return self._device.GetDeviceInfo().Name

    @property
    def backlash(self):
        return Decimal.ToDouble(self._device.GetBacklash())

    @backlash.setter
    def backlash(self, backlash: float):
        self._device.SetBacklash(Decimal(backlash))

    def stop(self):
        if self._device:
            self._device.Stop(0)
            print("Motion stopped")

    def move_abs(self, position: float):
        print(f"Moving to absolute position: {position}")
        position = Decimal(position)
        self._device.MoveTo(position, Int32(60000))
        time.sleep(2)  # Attends un peu pour voir si le mouvement se termine
        current_position = Decimal.ToDouble(self._device.GetPosition())
        print(f"Position after move: {current_position}")

    def move_rel(self, position: float):
        position = Decimal(position)
        self._device.MoveRelative(Generic.MotorDirection.Forward, position, Int32(60000))
        print(f"Moved relative by: {position}")

    def home(self):
        self._device.Home(0)
        print("Homing initiated")

    def get_position(self):
        if self._device:
            position = Decimal.ToDouble(self._device.GetPosition())
            print(f"Current position: {position}")
            return position
        return None

class KDC101(Kinesis):
    def __init__(self):
        super().__init__()
        print("KDC101 instance created")

    def connect(self, serial: str):
        if serial in serialnumbers_Kcube:
            print(f"Creating KCube DCServo with serial: {serial}")
            self._device = DCServo.KCubeDCServo.CreateKCubeDCServo(serial)
            super().connect(serial)
            if not self._device.IsSettingsInitialized():
                raise Exception("Device not initialized correctly")
            print("Device initialized successfully")
        else:
            raise ValueError('Invalid Serial Number')

class DAQ_Move_KDC101(DAQ_Move_base):
    _controller_units = 'degrees'
    _epsilon = 0.05
    is_multiaxes = False
    stage_names = []

    params = [{'title': 'Controller ID:', 'name': 'controller_id', 'type': 'str', 'value': '', 'readonly': True},
              {'title': 'Serial number:', 'name': 'serial_number', 'type': 'list', 'limits': serialnumbers_Kcube},
              ] + comon_parameters_fun(is_multiaxes, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: KDC101 = None
        print("Initializing attributes...")
        self.settings.child('bounds', 'is_bounds').setValue(True)
        self.settings.child('bounds', 'max_bound').setValue(20)
        self.settings.child('bounds', 'min_bound').setValue(0)
        print("Attributes initialized")

    def commit_settings(self, param):
        if param.name() == 'backlash':
            print(f"Committing backlash value: {param.value()}")
            self.controller.backlash = param.value()

    def ini_stage(self, controller=None):
        print("Initializing stage...")
        self.controller = self.ini_stage_init(controller, KDC101())

        if self.settings['multiaxes', 'multi_status'] == "Master":
            print(f"Connecting to controller with serial number: {self.settings['serial_number']}")
            self.controller.connect(self.settings['serial_number'])

        info = self.controller.name
        self.settings.child('controller_id').setValue(info)
        print(f"Stage initialized with info: {info}")

        initialized = True
        return info, initialized

    def close(self):
        if self.controller:
            print("Closing stage...")
            self.controller.close()
            print("Stage closed")

    def stop_motion(self):
        if self.controller:
            print("Stopping motion...")
            self.controller.stop()
            print("Motion stopped")

    def get_actuator_value(self):
        if self.controller:
            pos = self.controller.get_position()
            if pos is not None:
                pos = self.get_position_with_scaling(pos)
                print(f"Actuator value: {pos}")
                return pos
        return 0.0

    def move_abs(self, position):
        print(f"Moving to absolute position: {position}")
        position = self.check_bound(position)
        self.target_position = position
        position = self.set_position_with_scaling(position)
        print(f"Final position: {position}")

        if self.controller:
            self.controller.move_abs(position)

    def move_rel(self, position):
        print(f"Moving relative by position: {position}")
        position = self.check_bound(self.current_position + position) - self.current_position
        self.target_position = position + self.current_position
        position = self.set_position_relative_with_scaling(position)

        if self.controller:
            self.controller.move_rel(position)

    def move_home(self):
        print("Moving to home position")
        if self.controller:
            self.controller.home()

if __name__ == '__main__':
    main(__file__, init=False)
