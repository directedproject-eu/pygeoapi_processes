#!/bin/bash

# activate installed plugins
echo "\n[PythonPlugins]\nOS2DamageCost=true\nOS2DamageCostAdmin=true" >> /usr/share/qgis/resources/qgis_global_settings.ini

python3 /home/init_dtu_model.py