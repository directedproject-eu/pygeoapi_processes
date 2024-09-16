from qgis.core import QgsApplication

# ----------- #
# Basic setup #
# ----------- #
# QgsApplication.setPrefixPath("/usr", True)
# print("Prefix path:", QgsApplication.prefixPath())
print("Settings:\n", QgsApplication.showSettings())

qgs = QgsApplication([], False)
qgs.initQgis()

# ------------------- #
# Run example process #
# ------------------- #
from qgis.analysis import QgsNativeAlgorithms
import processing

processing.core.Processing.Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

print("Number of algorithms:", len(QgsApplication.processingRegistry().algorithms()))
print("Number of providers:", len(QgsApplication.processingRegistry().providers()))

# print("Start buffer process")
# print(processing.algorithmHelp("native:buffer"))
# result = processing.run("native:buffer", {'INPUT': 'osm_buildings_161124.gpkg', 'OUTPUT': 'buffered.gpkg'})
# print("Buffer process finished")
print("Start centroid process")
# print(processing.algorithmHelp("native:centroids"))
result = processing.run("native:centroids", {'INPUT': '/usr/share/qgis/resources/data/world_map.gpkg', 'OUTPUT': 'centroids.gpkg'})
print("Centroid process finished")

# ------------ #
# Clear memory #
# ------------ #
qgs.exitQgis()
