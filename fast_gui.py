import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import sys
import threading
import time
import math
import numpy as np


class DataProvider(threading.Thread):
    def __init__(self, update_interval=0.03):
        super(DataProvider, self).__init__()
        self.update_interval = update_interval
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.running = True
        self.theta = 0

    def run(self):
        idx = 0
        while self.running:
            x = math.sin(idx)
            y = math.cos(idx)
            z = math.sin(idx) * math.cos(idx)

            self.x_data.append(x)
            self.y_data.append(y)
            self.z_data.append(z)

            idx += 0.05
            time.sleep(self.update_interval)

    def stop(self):
        self.running = False


class MainWindow2D(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data_provider = DataProvider()
        self.data_provider.start()

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # Plot for X, Y, Z
        self.graphWidget_x = pg.PlotWidget()
        self.graphWidget_y = pg.PlotWidget()
        self.graphWidget_z = pg.PlotWidget()

        self.layout.addWidget(self.graphWidget_x)
        self.layout.addWidget(self.graphWidget_y)
        self.layout.addWidget(self.graphWidget_z)

        self.x_curve_1 = self.graphWidget_x.plot(pen='r', name="X_1")
        self.x_curve_2 = self.graphWidget_x.plot(pen='g', name="X_2")
        self.x_curve_3 = self.graphWidget_x.plot(pen='b', name="X_3")

        self.y_curve_1 = self.graphWidget_y.plot(pen='r', name="Y_1")
        self.y_curve_2 = self.graphWidget_y.plot(pen='g', name="Y_2")
        self.y_curve_3 = self.graphWidget_y.plot(pen='b', name="Y_3")

        self.z_curve_1 = self.graphWidget_z.plot(pen='r', name="Z_1")
        self.z_curve_2 = self.graphWidget_z.plot(pen='g', name="Z_2")
        self.z_curve_3 = self.graphWidget_z.plot(pen='b', name="Z_3")

        # Rotation data
        self.theta = 0

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)  # Update plot every 10 milliseconds

    def update_plot(self):
        # Update X, Y, Z plots
        self.x_curve_1.setData(self.data_provider.x_data[-100:])
        self.y_curve_1.setData(self.data_provider.y_data[-100:])
        self.z_curve_1.setData(self.data_provider.z_data[-100:])

        self.x_curve_2.setData([i * 0.5 for i in self.data_provider.x_data[-100:]])
        self.y_curve_2.setData([i * 0.5 for i in self.data_provider.y_data[-100:]])
        self.z_curve_2.setData([i * 0.5 for i in self.data_provider.z_data[-100:]])

        self.x_curve_3.setData([i * 0.1 for i in self.data_provider.x_data[-100:]])
        self.y_curve_3.setData([i * 0.1 for i in self.data_provider.y_data[-100:]])
        self.z_curve_3.setData([i * 0.1 for i in self.data_provider.z_data[-100:]])

    def closeEvent(self, event):
        self.data_provider.stop()
        self.data_provider.join()
        event.accept()


class MainWindow3D(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data_provider = DataProvider()
        self.data_provider.start()

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # 3D Plot
        self.graphWidget_3d = gl.GLViewWidget()
        self.graphWidget_3d.opts['distance'] = 40
        self.graphWidget_3d.setWindowTitle('3D Coordinate System')
        self.layout.addWidget(self.graphWidget_3d)

        # Rotation data
        self.theta = 0
        self.gamma = 0

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)  # Update plot every 10 milliseconds

    def rotate_coords(self, coords, theta, gamma):
        """
        Rotate coordinates around the origin by an angle theta in 3D space.

        Args:
            coords (np.array): Array of shape (N, 3) representing coordinates in 3D space.
            theta (float): Angle in radians by which to rotate the coordinates.

        Returns:
            np.array: Rotated coordinates.
        """
        # Rotation matrix around the x-axis
        R_x = np.array([[1, 0, 0],
                        [0, np.cos(theta), -np.sin(theta)],
                        [0, np.sin(theta), np.cos(theta)]])

        # Rotation matrix around the y-axis
        R_y = np.array([[np.cos(gamma), 0, np.sin(gamma)],
                        [0, 1, 0],
                        [-np.sin(gamma), 0, np.cos(gamma)]])

        # Rotation matrix around the z-axis
        R_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta), np.cos(theta), 0],
                        [0, 0, 1]])

        # Rotate coordinates around the x-axis
        coords = np.dot(coords, R_x.T)

        # Rotate coordinates around the y-axis
        coords = np.dot(coords, R_y.T)

        # Rotate coordinates around the z-axis
        #coords = np.dot(coords, R_z.T)

        return coords

    def update_plot(self):
        # Update 3D plot
        self.theta += 0.1
        self.gamma += 0.02
        self.graphWidget_3d.items.clear()
        if(self.theta >= 2*math.pi):
            self.theta -= 2*math.pi
        #coords = np.array([self.rotate_coords([0, 0, 0], self.theta), self.rotate_coords([10.0, 0, 0], self.theta),
        #                  self.rotate_coords([0, 10.0, 0], self.theta), self.rotate_coords([0, 0, 10.0], self.theta)])
        coords = self.rotate_coords([[0,0,0], [10.0,0,0], [0,10.0,0],[0,0,10.0]], self.theta,self.gamma)
        #print(coords)
        #coords = self.rotate_coords(coords, self.theta)
        lines = [[0, 1], [0, 2], [0, 3]]
        colors = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]

        for line, color in zip(lines, colors):
            line_item = gl.GLLinePlotItem(pos=coords[line], color=color, width=5)
            self.graphWidget_3d.addItem(line_item)

        #self.add_arrow()

        self.graphWidget_3d.opts['rotation'] = (self.theta, 0, 0)

    def add_arrow(self):
        # Generate arrow geometry
        arrow_length = 0.5
        arrow_pos = np.array([[0, 0, 0], [arrow_length, 0, 0]])
        arrow_color = (0, 0, 1, 1)  # Blue color
        arrow_item = gl.GLLinePlotItem(pos=arrow_pos, color=arrow_color, width=5)
        self.graphWidget_3d.addItem(arrow_item)

    def closeEvent(self, event):
        self.data_provider.stop()
        self.data_provider.join()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and show 2D window
    window2d = MainWindow2D()
    window2d.resize(800, 600)
    window2d.show()

    # Create and show 3D window
    window3d = MainWindow3D()
    window3d.resize(800, 600)
    window3d.show()

    sys.exit(app.exec_())
