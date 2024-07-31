pymodaq_plugins_KDC101
======================


Description
===========

Ce projet permet d'intégrer un moteur Thorlabs KDC101 au module PyMoDAQ à partir du template `pymodaq_plugins_template <https://github.com/PyMoDAQ/pymodaq_plugins_template>`_. Il est important de suivre et renommer le projet comme expliqué sur `le tutoriel PyMoDAQ <http://pymodaq.cnrs.fr/en/latest/tutorials/new_plugin.html>`_. Ce projet utilise les librairies DLL du wrapper disponible sur le site de Thorlabs.

Authors
=======

* Enzo Sebiane (enzo.sebiane@orange.fr)

Instruments
===========

Actuators
+++++++++

* **KDC101**: contrôle du moteur Thorlabs KDC101

Installation instructions
=========================

1. **Version de PyMoDAQ**: Assurez-vous d'utiliser la dernière version de PyMoDAQ.
2. **Système d'exploitation**: Ce plugin a été testé sur Windows 10.
3. **Drivers du fabricant**: Installez les drivers Thorlabs Kinesis disponibles sur le site de Thorlabs pour que ce plugin fonctionne correctement.

Utilisation
===========

Pour utiliser ce plugin, suivez les étapes ci-dessous :

1. Clonez le dépôt PyMoDAQ :

    .. code-block:: bash

        git clone https://github.com/PyMoDAQ/PyMoDAQ.git

2. Installez le plugin via pip :

    .. code-block:: bash

        pip install pymodaq-plugins-KDC101

Utilisez ce template pour créer un dépôt sur votre compte et commencez le développement de votre propre plugin PyMoDAQ !

Instructions pour renommer le projet
====================================

Suivez les instructions détaillées dans le tutoriel `PyMoDAQ <http://pymodaq.cnrs.fr/en/latest/tutorials/new_plugin.html>`_ pour renommer correctement le projet et ajuster les configurations nécessaires.

Création et Publication sur PyPI
================================

Pour créer et publier votre librairie sur PyPI, suivez ces étapes :

1. Assurez-vous d'avoir les fichiers ``setup.py``, ``README.md``, et autres fichiers nécessaires à la racine de votre projet.
2. Créez une distribution source et une distribution binaire de votre package :

    .. code-block:: bash

        python setup.py sdist bdist_wheel

3. Installez ``twine`` si ce n'est pas déjà fait :

    .. code-block:: bash

        pip install twine

4. Téléchargez les distributions sur PyPI en utilisant ``twine`` :

    .. code-block:: bash

        twine upload dist/*

    Vous serez invité à entrer vos informations d'identification PyPI (nom d'utilisateur et mot de passe).

Contributeurs
=============

* Enzo Sebiane
