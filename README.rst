pymodaq_plugins_KDC_101
########################



Description
===========

This project integrates a Thorlabs KDC101 motor into the PyMoDAQ module based on the `pymodaq_plugins_template <https://github.com/PyMoDAQ/pymodaq_plugins_template>`_ template. To use this plugin, ensure you are using the latest version of PyMoDAQ, and have Windows 10 as the operating system. Install the Thorlabs Kinesis drivers available on Thorlabs' website for proper functionality. For usage, clone the PyMoDAQ repository using `git clone https://github.com/PyMoDAQ/PyMoDAQ.git` and install the plugin via `pip install pymodaq-plugins-KDC101`. To create and publish on PyPI, ensure you have the `setup.py`, `README.rst`, and other necessary files at the root of your project. Create a source and binary distribution with `python setup.py sdist bdist_wheel`, install `twine` with `pip install twine`, and upload distributions to PyPI using `twine upload dist/*`.

Pyodaq version -- 4.2.4

1. **Téléchargement des logiciels nécessaires** :

   - Rendez-vous sur `la page de téléchargement Thorlabs <https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=Motion_Control>`_ et téléchargez le logiciel Kinesis : **Kinesis 64-Bit Software pour Windows 64-Bit**.


2. **Installation du plugin** :

   - Dans l'invite de commande Anaconda, exécutez la commande suivante :

   .. code-block:: bash

       pip install pymodaq-plugins-KDC101

Authors
=======

* Enzo Sebiane (enzo.sebiane@orange.fr)

Instruments
===========

**KDC101**: Control of the Thorlabs KDC101 motor.

Actuators
+++++++++

* **KDC101**

Viewer0D
++++++++

Viewer1D
++++++++

Viewer2D
++++++++
