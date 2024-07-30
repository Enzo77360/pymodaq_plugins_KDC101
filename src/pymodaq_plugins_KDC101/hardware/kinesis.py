import clr
import os
import sys
import time
from System import Decimal, Int32

# Importer les bibliothèques Kinesis
dll_path = r'C:\Program Files\Thorlabs\Kinesis'
if dll_path not in sys.path:
    sys.path.append(dll_path)

clr.AddReference('Thorlabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.KCube.DCServoCLI')
clr.AddReference('Thorlabs.MotionControl.GenericMotorCLI')

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import VelocityParameters

class KCubeDCServoController:
    def __init__(self):
        # Initialiser le gestionnaire de périphériques
        DeviceManagerCLI.BuildDeviceList()

        # Obtenir la liste des périphériques
        self.device_list = DeviceManagerCLI.GetDeviceList()

        # Convertir la liste en liste Python pour un affichage correct
        self.device_list_python = [str(device) for device in self.device_list]

        # Initialiser l'ID du périphérique à None
        self.device_id = None
        self.motor = None
        self.distance_total = None
        self.temps_total_s = 0.0
        self.temps_total_s_d = None
        self.vitesse = None
        self.distance_precedente = None # Distance précédente initialisée à zéro

    def get_device_list(self):
        return self.device_list_python

    def connect_motor(self, device_id):
        # Vérifier que le périphérique est détecté
        if device_id not in self.device_list_python:
            raise Exception(f"Le périphérique avec l'ID {device_id} n'est pas détecté.")

        # Connecter au périphérique
        self.device_id = device_id
        self.motor = KCubeDCServo.CreateKCubeDCServo(self.device_id)
        self.motor.Connect(self.device_id)

    def initialize_motor(self):
        # Initialiser le moteur
        print('Initialisation du moteur...')
        self.motor.LoadMotorConfiguration(self.device_id)
        self.motor.StartPolling(250)
        self.motor.EnableDevice()
        self.motor.Home(60000)  # Temporisation de 60 secondes pour l'opération de homing

    def configure_movement(self, distance_total_mm, temps_total_s):
        # Calculer la vitesse en mm/s
        vitesse_mm_s = 2.0 #distance_total_mm / temps_total_s

        # Convertir en Decimal pour les opérations
        self.distance_total = Decimal(distance_total_mm)
        self.temps_total_s_d = Decimal(temps_total_s)

        # Calculer la vitesse en mm/s
        self.vitesse = Decimal(vitesse_mm_s)

        # Configurer les paramètres de vitesse
        velocity_params = self.motor.GetVelocityParams()
        velocity_params.MaxVelocity = self.vitesse
        self.motor.SetVelocityParams(velocity_params)

    def move_motor(self):
        # Démarrer le mouvement
        print(f'Déplacement de {self.distance_total} mm à une vitesse de {self.vitesse} mm/s')
        self.motor.MoveTo(self.distance_total, Int32(60000))


    def wait_for_completion(self):
        # Attendre la fin du mouvement
        time.sleep(float(self.temps_total_s) + 1.0)  # On attend légèrement plus que le temps total pour être sûr que le mouvement soit terminé

    def disconnect_motor(self):
        # Déconnecter le périphérique
        self.motor.StopPolling()
        self.motor.Disconnect()
        print("Mouvements terminés.")