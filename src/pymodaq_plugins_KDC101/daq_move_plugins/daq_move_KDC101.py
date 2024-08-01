from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun, main,
                                                          DataActuatorType, DataActuator)
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.parameter import Parameter
from ctypes import cdll, c_int, c_double, byref
import clr
import os
import sys
from pymodaq_plugins_KDC101.hardware.kinesis import KCubeDCServoController


class DAQ_Move_KDC101(DAQ_Move_base):
    _controller_units = 'degrees'
    _epsilon = 0.05
    is_multiaxes = False
    stage_names = []

    params = [{'title': 'Controller ID:', 'name': 'controller_id', 'type': 'str', 'value': '', 'readonly': True},
              {'title': 'Serial number:', 'name': 'serial_number', 'type': 'list',
               'limits': []},  # Ajustez cette valeur en fonction des numéros de série disponibles
              {'title': 'Backlash:', 'name': 'backlash', 'type': 'float', 'value': 0, },
              ] + comon_parameters_fun(is_multiaxes, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: KCubeDCServoController = None
        self.settings.child('bounds', 'is_bounds').setValue(True)
        self.settings.child('bounds', 'max_bound').setValue(360)
        self.settings.child('bounds', 'min_bound').setValue(0)

    def commit_settings(self, param):
        if param.name() == 'backlash':
            self.controller.backlash = param.value()

    def ini_stage(self, controller=None):
        self.controller = self.ini_stage_init(controller, KCubeDCServoController())

        if self.settings['multiaxes', 'multi_status'] == "Master":
            self.controller.connect_motor(self.settings['serial_number'])

        info = self.controller.name
        self.settings.child('controller_id').setValue(info)

        self.controller.backlash = self.settings['backlash']

        initialized = True
        return info, initialized

    def close(self):
        """Close the current instance of Kinesis instrument."""
        if self.controller is not None:
            self.controller.disconnect_motor()

    def stop_motion(self):
        """Stop the current motion."""
        if self.controller is not None:
            self.controller.stop()

    def get_actuator_value(self):
        """Get the current hardware position."""
        pos = self.controller.get_position()
        pos = self.get_position_with_scaling(pos)
        return pos

    def move_abs(self, position):
        """Move to an absolute position."""
        position = self.check_bound(position)
        self.target_position = position
        position = self.set_position_with_scaling(position)

        self.controller.move_motor()

    def move_rel(self, position):
        """Move relative to the current position."""
        position = self.check_bound(self.current_position + position) - self.current_position
        self.target_position = position + self.current_position
        position = self.set_position_relative_with_scaling(position)

        self.controller.move_motor()

    def move_home(self):
        """Move to the home position."""
        self.controller.initialize_motor()
        self.controller.home(callback=self.move_done)


if __name__ == '__main__':
    main(__file__, init=False)
