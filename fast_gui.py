import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from data import SensorData
from processing import SensorHistory, Derivation3, Event3
import sys
import math
import numpy as np


class MainWindow2D(QMainWindow):
    def __init__(self, history_length = 100):
        super().__init__()

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # defines number of historic line entries to stored and visualized
        self.history_length = history_length

        # Plot for X, Y, Z
        self.graph_widget_rot = pg.PlotWidget()
        self.graph_widget_acc = pg.PlotWidget()
        self.graph_widget_gyro = pg.PlotWidget()
        self.graph_widget_gyro_deriv = pg.PlotWidget()

        self.layout.addWidget(self.graph_widget_rot)
        self.layout.addWidget(self.graph_widget_acc)
        self.layout.addWidget(self.graph_widget_gyro)
        self.layout.addWidget(self.graph_widget_gyro_deriv)

        self.rot_curve_x = self.graph_widget_rot.plot(pen='r', name="ROT_X")
        self.rot_curve_y = self.graph_widget_rot.plot(pen='g', name="ROT_Y")
        self.rot_curve_z = self.graph_widget_rot.plot(pen='b', name="ROT_Z")

        self.acc_curve_x = self.graph_widget_acc.plot(pen='r', name="ACC_X")
        self.acc_curve_y = self.graph_widget_acc.plot(pen='g', name="ACC_Y")
        self.acc_curve_z = self.graph_widget_acc.plot(pen='b', name="ACC_Z")

        self.gyro_curve_x = self.graph_widget_gyro.plot(pen='r', name="GYRO_X")
        self.gyro_curve_y = self.graph_widget_gyro.plot(pen='g', name="GYRO_Y")
        self.gyro_curve_z = self.graph_widget_gyro.plot(pen='b', name="GYRO_Z")

        self.gyro_derivation_x = self.graph_widget_gyro_deriv.plot(pen='r', name="GYRO_DERIV_X")
        self.gyro_derivation_y = self.graph_widget_gyro_deriv.plot(pen='g', name="GYRO_DERIV_Y")
        self.gyro_derivation_z = self.graph_widget_gyro_deriv.plot(pen='b', name="GYRO_DERIV_Z")
        self.gyro_derivation_events = self.graph_widget_gyro_deriv.plot(pen=None, symbol='+', name="GYRO_DERIV_Events")

        self.history = SensorHistory(history_length)
        self.gyro_derivation = Derivation3(history_length, True)

    async def update_plot(self, data: SensorData):
        self.history.append(data)
        self.gyro_derivation.append(data.gyro, data.time)

        # Update X, Y, Z plots
        self.rot_curve_x.setData(self.history.rot.t, self.history.rot.x)
        self.rot_curve_y.setData(self.history.rot.t,self.history.rot.y)
        self.rot_curve_z.setData(self.history.rot.t, self.history.rot.z)

        self.acc_curve_x.setData(self.history.acc.t, self.history.acc.x)
        self.acc_curve_y.setData(self.history.acc.t, self.history.acc.y)
        self.acc_curve_z.setData(self.history.acc.t, self.history.acc.z)

        self.gyro_curve_x.setData(self.history.gyro.t, self.history.gyro.x)
        self.gyro_curve_y.setData(self.history.gyro.t, self.history.gyro.y)
        self.gyro_curve_z.setData(self.history.gyro.t, self.history.gyro.z)

        self.gyro_derivation_x.setData(self.gyro_derivation.t, self.gyro_derivation.x)
        self.gyro_derivation_y.setData(self.gyro_derivation.t, self.gyro_derivation.y)
        self.gyro_derivation_z.setData(self.gyro_derivation.t, self.gyro_derivation.z)

    async def event_triggered(self, events: [Event3]):
        event_x = []
        event_y = []
        for e in events:
            event_x.append(e.position)
            event_y.append(e.value)
        self.gyro_derivation_events.setData(event_x, event_y)

class MainWindow3D(QMainWindow):
    def __init__(self):
        super().__init__()

        self.device = None

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        # 3D Plot
        self.graphWidget_3d = gl.GLViewWidget()
        self.graphWidget_3d.opts['distance'] = 40
        self.graphWidget_3d.setWindowTitle('3D Coordinate System')
        self.layout.addWidget(self.graphWidget_3d)

        # Rotation data
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        # self.timer = pg.QtCore.QTimer()
        # self.timer.timeout.connect(self.update_plot)
        # self.timer.start(30)  # Update plot every 10 milliseconds

    def rotate_coords(self, coords, alpha, beta, gamma):
        """
        Rotate coordinates around the origin by an angle alpha in 3D space.

        Args:
            coords (np.array): Array of shape (N, 3) representing coordinates in 3D space.
            alpha (float): Angle in radians by which to rotate the coordinates around x.
            beta (float): Angle in radians by which to rotate the coordinates around y.
            gamma (float): Angle in radians by which to rotate the coordinates around z.

        Returns:
            np.array: Rotated coordinates.
        """
        # Rotation matrix around the x-axis
        R_x = np.array([[1, 0, 0],
                        [0, np.cos(alpha), -np.sin(alpha)],
                        [0, np.sin(alpha), np.cos(alpha)]])

        # Rotation matrix around the y-axis
        R_y = np.array([[np.cos(beta), 0, np.sin(beta)],
                        [0, 1, 0],
                        [-np.sin(beta), 0, np.cos(beta)]])

        # Rotation matrix around the z-axis
        R_z = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                        [np.sin(gamma), np.cos(gamma), 0],
                        [0, 0, 1]])

        # Rotate coordinates around the x-axis
        coords = np.dot(coords, R_x.T)

        # Rotate coordinates around the y-axis
        coords = np.dot(coords, R_y.T)

        # Rotate coordinates around the z-axis
        coords = np.dot(coords, R_z.T)

        return coords

    async def update_plot(self, data : SensorData):
        # Update 3D plot
        self.alpha = data.rot.x * math.pi / 180.0
        self.beta = data.rot.y * math.pi / 180.0
        self.gamma = data.rot.z * math.pi / 180.0
        self.graphWidget_3d.items.clear()
        if (self.alpha >= 2 * math.pi):
            self.alpha -= 2 * math.pi
        if (self.beta >= 2 * math.pi):
            self.beta -= 2 * math.pi
        if (self.gamma >= 2 * math.pi):
            self.gamma -= 2 * math.pi
        if (self.alpha < 0):
            self.alpha += 2 * math.pi
        if (self.beta < 0):
            self.beta += 2 * math.pi
        if (self.gamma < 0):
            self.gamma += 2 * math.pi
        # coords = np.array([self.rotate_coords([0, 0, 0], self.alpha), self.rotate_coords([10.0, 0, 0], self.alpha),
        #                  self.rotate_coords([0, 10.0, 0], self.alpha), self.rotate_coords([0, 0, 10.0], self.alpha)])
        coords = self.rotate_coords([[0, 0, 0], [10.0, 0, 0], [0, 10.0, 0], [0, 0, 10.0]], self.alpha, self.beta,
                                    self.gamma)
        # print(coords)
        # coords = self.rotate_coords(coords, self.alpha)
        lines = [[0, 1], [0, 2], [0, 3]]
        colors = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]

        for line, color in zip(lines, colors):
            line_item = gl.GLLinePlotItem(pos=coords[line], color=color, width=5)
            self.graphWidget_3d.addItem(line_item)

        # self.add_arrow()

        self.graphWidget_3d.opts['rotation'] = (0, 0, 0)

    def add_arrow(self):
        # Generate arrow geometry
        arrow_length = 0.5
        arrow_pos = np.array([[0, 0, 0], [arrow_length, 0, 0]])
        arrow_color = (0, 0, 1, 1)  # Blue color
        arrow_item = gl.GLLinePlotItem(pos=arrow_pos, color=arrow_color, width=5)
        self.graphWidget_3d.addItem(arrow_item)


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

    window3d.update_plot(0, 0, 0)

    sys.exit(app.exec_())
