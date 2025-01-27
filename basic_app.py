import sys
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem
)
from qgis.gui import QgsMapCanvas, QgsMapTool
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt

class MouseTracker(QgsMapTool):
    def __init__(self, canvas, label):
        super().__init__(canvas)
        self.canvas = canvas
        self.label = label

    def canvasMoveEvent(self, event):
        # Get mouse coordinates in map units
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y())
        # Update label with the coordinates
        self.label.setText(f"Mouse Coordinates: ({point.x():.6f}, {point.y():.6f})")


class QGISStandaloneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt App with QGIS Canvas")
        self.setGeometry(100, 100, 800, 600)

        # Initialize QGIS Map Canvas
        self.canvas = QgsMapCanvas()

        crs = QgsCoordinateReferenceSystem(4326)
        self.project = QgsProject.instance()
        self.canvas.setDestinationCrs(crs)

        # Set up the layout
        main_layout = QVBoxLayout()
        canvas_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        canvas_layout.addWidget(self.canvas)

        self.label = QLabel("Mouse Coordinates: (0, 0)", self)
        self.label.setAlignment(Qt.AlignCenter)

        # Set up the mouse tracking tool
        self.mouse_tracker = MouseTracker(self.canvas, self.label)
        self.canvas.setMapTool(self.mouse_tracker)

        # Add widgets to the bottom layout
        bottom_layout.addWidget(self.label)

        # Add button to add a GeoJSON layer
        self.add_layer_button = QPushButton("Add GeoJSON Layer", self)
        self.add_layer_button.clicked.connect(self.add_geojson_layer)
        bottom_layout.addWidget(self.add_layer_button)

        main_layout.addLayout(canvas_layout)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load layers
        self.load_layer()

    def add_geojson_layer(self):
        # Example: Load a shapefile layer
        layer_path = "sample_geojson/add_points.geojson"
        layer = QgsVectorLayer(layer_path, "Add Points", "ogr")
        if not layer.isValid():
            print(f"Failed to load layer: {layer_path}")
            return

        # Add layer to the QGIS project
        self.project.addMapLayer(layer)

        # Set layer style
        symbol = layer.renderer().symbol()
        symbol.setColor(Qt.blue)

        # Add basemap
        layers = self.canvas.layers()
        layers = [layer] + layers
        self.canvas.setLayers(layers)

    def load_layer(self):
        # Example: Load a shapefile layer
        layer_path = "sample_geojson/tlv_Ride.geojson"
        layer = QgsVectorLayer(layer_path, "TLV Ride", "ogr")
        if not layer.isValid():
            print(f"Failed to load layer: {layer_path}")
            return

        # Add layer to the QGIS project
        self.project.addMapLayer(layer)

        # Set layer style
        symbol = layer.renderer().symbol()
        symbol.setColor(Qt.red)
        symbol.setWidth(2)

        # Display the layer on the canvas
        self.canvas.setLayers([layer])
        self.canvas.zoomToFullExtent()
        # Add basemap
        basemap = self.add_basemap()
        self.canvas.setLayers([layer, basemap])

    def add_basemap(self):
        # OpenStreetMap XYZ Tile Layer URL
        url = 'crs=EPSG:4326&format=image/png&type=xyz&url=http://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png'
        basemap = QgsRasterLayer(url, "OpenStreetMap", "wms", QgsRasterLayer.LayerOptions())
        if basemap.isValid():
            self.project.addMapLayer(basemap)
            return basemap
        else:
            print("Failed to load basemap!")

def main():
    # Initialize QGIS Application
    QgsApplication.setPrefixPath('/Applications/QGIS-LTR.app', True)

    qgis_app = QgsApplication([], False)
    qgis_app.initQgis()

    # Initialize PyQt Application
    app = QApplication(sys.argv)
    main_window = QGISStandaloneApp()
    main_window.show()

    # Execute the application
    app.exec_()

    # Exit QGIS
    qgis_app.exitQgis()

if __name__ == "__main__":
    main()
