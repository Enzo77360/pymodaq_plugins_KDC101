from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun, main,
                                                          DataActuatorType, DataActuator)
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.parameter import Parameter
from ctypes import cdll, c_int, c_double, byref
import time
import os
import sys

class PythonWrapperOf_KDC101:
    def __init__(self, dll_path, serial_num):
        self.lib = cdll.LoadLibrary(dll_path)
        self.serial_num = serial_num

    def build_device_list(self):
        return self.lib.TLI_BuildDeviceList()

    def open(self):
        return self.lib.CC_Open(self.serial_num)

    def start_polling(self, interval):
        self.lib.CC_StartPolling(self.serial_num, c_int(interval))

    def home(self):
        self.lib.CC_Home(self.serial_num)

    def set_motor_params_ext(self, steps_per_rev, gbox_ratio, pitch):
        self.lib.CC_SetMotorParamsExt(self.serial_num, c_double(steps_per_rev), c_double(gbox_ratio), c_double(pitch))

    def request_position(self):
        self.lib.CC_RequestPosition(self.serial_num)

    def get_position(self):
        return self.lib.CC_GetPosition(self.serial_num)

    def get_real_value_from_device_unit(self, dev_pos):
        real_pos = c_double()
        self.lib.CC_GetRealValueFromDeviceUnit(self.serial_num, dev_pos, byref(real_pos), 0)
        return real_pos.value

    def close(self):
        self.lib.CC_Close(self.serial_num)


class DAQ_Move_KDC101(DAQ_Move_base):
    _controller_units = 'whatever'
    is_multiaxes = False
    _axis_names = ['Axis1']
    _epsilon = 0.1
    data_actuator_type = DataActuatorType['float']  # Assuming 'float' is the correct type

    params = comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)
        self.ini_attributes()

    def ini_attributes(self):
        self.controller: PythonWrapperOf_KDC101 = None
        self.lib = None
        self.serial_num = b"27500125"  # Replace with your actual serial number
        self.STEPS_PER_REV = 1919.64186
        self.gbox_ratio = 1.0
        self.pitch = 1.0

    def get_actuator_value(self):
        self.controller.request_position()
        time.sleep(0.2)
        dev_pos = self.controller.get_position()
        real_pos = self.controller.get_real_value_from_device_unit(dev_pos)
        pos = DataActuator(data=[real_pos])  # DataActuator expects a list of data
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        if self.controller:
            self.controller.close()

    def commit_settings(self, param: Parameter):
        # Implement if parameters need to be committed
        pass

    def ini_stage(self, controller=None):
        """Initialize the KDC101 controller and configure it."""
        try:
            # Ensure the DLL directory is set correctly
            if sys.version_info < (3, 8):
                os.chdir(r"C:\Program Files\Thorlabs\Kinesis")
            else:
                os.add_dll_directory(r"C:\Program Files\Thorlabs\Kinesis")

            # Initialize the KDC101 controller
            self.controller = PythonWrapperOf_KDC101("Thorlabs.MotionControl.KCube.DCServo.dll", self.serial_num)
            if self.controller.build_device_list() == 0:
                if self.controller.open() == 0:
                    self.controller.start_polling(200)
                    time.sleep(1)
                    self.controller.home()
                    time.sleep(1)
                    self.controller.set_motor_params_ext(self.STEPS_PER_REV, self.gbox_ratio, self.pitch)
                    self.controller.request_position()
                    time.sleep(0.2)
                    dev_pos = self.controller.get_position()
                    real_pos = self.controller.get_real_value_from_device_unit(dev_pos)
                    print(f'Current position: {real_pos}')
                    return "KDC101 initialized.", True
                else:
                    return "Failed to open KDC101 device.", False
            else:
                return "Failed to build device list.", False
        except Exception as e:
            return f"Exception occurred: {str(e)}", False

    def move_abs(self, value: DataActuator):
        """Move to an absolute position."""
        value = self.check_bound(value)
        self.target_value = value
        value = self.set_position_with_scaling(value)
        try:
            new_pos_dev = c_int()
            self.lib.CC_GetDeviceUnitFromRealValue(self.serial_num, c_double(value.data[0]), byref(new_pos_dev), 0)
            self.lib.CC_SetMoveAbsolutePosition(self.serial_num, new_pos_dev)
            time.sleep(0.25)
            self.lib.CC_MoveAbsolute(self.serial_num)
            self.emit_status(ThreadCommand('Update_Status', ['Moved to absolute position']))
        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [f"Move absolute failed: {str(e)}"]))

    def move_rel(self, value: DataActuator):
        """Move to a relative position."""
        value = self.check_bound(self.current_position + value.data[0]) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)
        try:
            current_pos = self.lib.CC_GetPosition(self.serial_num)
            new_pos_dev = c_int(int(current_pos + value.data[0]))
            self.lib.CC_SetMoveAbsolutePosition(self.serial_num, new_pos_dev)
            time.sleep(0.25)
            self.lib.CC_MoveAbsolute(self.serial_num)
            self.emit_status(ThreadCommand('Update_Status', ['Moved relative position']))
        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [f"Move relative failed: {str(e)}"]))

    def move_home(self):
        """Move to the home position."""
        try:
            self.lib.CC_Home(self.serial_num)
            self.emit_status(ThreadCommand('Update_Status', ['Homing complete']))
        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [f"Homing failed: {str(e)}"]))

    def stop_motion(self):
        """Stop any ongoing motion."""
        try:
            self.lib.CC_StopImmediate(self.serial_num)
            self.emit_status(ThreadCommand('Update_Status', ['Motion stopped']))
        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [f"Stop motion failed: {str(e)}"]))


if __name__ == '__main__':
    main(__file__)