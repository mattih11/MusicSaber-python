import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import threading

class Gui:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(311, projection='3d')
        self.ax_acc = self.fig.add_subplot(3, 1, 2)
        self.ax_gyr = self.fig.add_subplot(3, 1, 3)
        self.acc_history = {'x': [], 'y': [], 'z': []}
        self.gyr_history = {'x': [], 'y': [], 'z': []}
        self.lock = threading.Lock()

    def update(self, orientation_angles, mag_data, acc_data, gyr_data):
        with self.lock:
            self.ax.cla()
            self.ax.set_xlim(-1, 1)
            self.ax.set_ylim(-1, 1)
            self.ax.set_zlim(-1, 1)
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')

            # Rotation um alle drei Achsen
            xy_angle_rad = np.radians(orientation_angles['xy'])
            xz_angle_rad = np.radians(orientation_angles['xz'])
            yz_angle_rad = np.radians(orientation_angles['yz'])

            combined_rotation_matrix = np.dot(self.rotation_matrix_y(xy_angle_rad),
                                              np.dot(self.rotation_matrix_x(xz_angle_rad),
                                                     self.rotation_matrix_z(yz_angle_rad)))

            # Berechnung der rotierten Achsen
            rotated_x = np.dot(combined_rotation_matrix, [1, 0, 0])
            rotated_y = np.dot(combined_rotation_matrix, [0, 1, 0])
            rotated_z = np.dot(combined_rotation_matrix, [0, 0, 1])

            # Darstellung der rotierten Achsen
            self.ax.quiver(0, 0, 0, rotated_x[0], rotated_x[1], rotated_x[2], color='r', arrow_length_ratio=0.1)
            self.ax.quiver(0, 0, 0, rotated_y[0], rotated_y[1], rotated_y[2], color='g', arrow_length_ratio=0.1)
            self.ax.quiver(0, 0, 0, rotated_z[0], rotated_z[1], rotated_z[2], color='b', arrow_length_ratio=0.1)

            # Anzeige der Winkelwerte als Textannotationen
            self.ax.text(rotated_x[0], rotated_x[1], rotated_x[2], '{:.2f}°'.format(orientation_angles["xy"]), color='r', fontsize=8)
            self.ax.text(rotated_y[0], rotated_y[1], rotated_y[2], '{:.2f}°'.format(orientation_angles["xz"]), color='g', fontsize=8)
            self.ax.text(rotated_z[0], rotated_z[1], rotated_z[2], '{:.2f}°'.format(orientation_angles["yz"]), color='b', fontsize=8)

            # Anzeige der Rohwerte der Magnetometerdaten als Textannotationen
            self.ax.text(1.1, 0, 0, f'mag.x: {mag_data["x"]}', color='r', fontsize=8)
            self.ax.text(0, 1.1, 0, f'mag.y: {mag_data["y"]}', color='g', fontsize=8)
            self.ax.text(0, 0, 1.1, f'mag.z: {mag_data["z"]}', color='b', fontsize=8)

            # Plot der Beschleunigungsdaten
            self.acc_history['x'].append(acc_data['x'])
            self.acc_history['y'].append(acc_data['y'])
            self.acc_history['z'].append(acc_data['z'])

            if len(self.acc_history['x']) > 100:
                for axis in self.acc_history:
                    self.acc_history[axis] = self.acc_history[axis][-100:]

            self.ax_acc.cla()
            self.ax_acc.plot(range(len(self.acc_history['x'])), self.acc_history['x'], color='r', label='acc_x')
            self.ax_acc.plot(range(len(self.acc_history['y'])), self.acc_history['y'], color='g', label='acc_y')
            self.ax_acc.plot(range(len(self.acc_history['z'])), self.acc_history['z'], color='b', label='acc_z')
            self.ax_acc.axhline(y=acc_data['x'], color='r', linestyle='--', linewidth=0.5)
            self.ax_acc.axhline(y=acc_data['y'], color='g', linestyle='--', linewidth=0.5)
            self.ax_acc.axhline(y=acc_data['z'], color='b', linestyle='--', linewidth=0.5)
            self.ax_acc.set_xlabel('Time')
            self.ax_acc.set_ylabel('Acceleration')
            self.ax_acc.legend()

            # Plot der Gyroskopdaten
            self.gyr_history['y'].append(gyr_data['y'])
            self.gyr_history['z'].append(gyr_data['z'])
            self.gyr_history['x'].append(gyr_data['x'])

            if len(self.gyr_history['x']) > 100:
                for axis in self.gyr_history:
                    self.gyr_history[axis] = self.gyr_history[axis][-100:]

            self.ax_gyr.cla()
            self.ax_gyr.plot(range(len(self.gyr_history['x'])), self.gyr_history['x'], color='r', label='gyr_x')
            self.ax_gyr.plot(range(len(self.gyr_history['y'])), self.gyr_history['y'], color='g', label='gyr_y')
            self.ax_gyr.plot(range(len(self.gyr_history['z'])), self.gyr_history['z'], color='b', label='gyr_z')
            self.ax_gyr.axhline(y=gyr_data['x'], color='r', linestyle='--', linewidth=0.5)
            self.ax_gyr.axhline(y=gyr_data['y'], color='g', linestyle='--', linewidth=0.5)
            self.ax_gyr.axhline(y=gyr_data['z'], color='b', linestyle='--', linewidth=0.5)
            self.ax_gyr.set_xlabel('Time')
            self.ax_gyr.set_ylabel('angular acceleration')
            self.ax_gyr.legend()

            plt.draw()
            plt.pause(0.001)

    def update_async(self, orientation_angles, mag_data, acc_data, gyr_data):
        threading.Thread(target=self.update, args=(orientation_angles, mag_data, acc_data, gyr_data)).start()


    def rotation_matrix_x(self, angle):
        return np.array([[1, 0, 0],
                         [0, np.cos(angle), -np.sin(angle)],
                         [0, np.sin(angle), np.cos(angle)]])

    def rotation_matrix_y(self, angle):
        return np.array([[np.cos(angle), 0, np.sin(angle)],
                         [0, 1, 0],
                         [-np.sin(angle), 0, np.cos(angle)]])

    def rotation_matrix_z(self, angle):
        return np.array([[np.cos(angle), -np.sin(angle), 0],
                         [np.sin(angle), np.cos(angle), 0],
                         [0, 0, 1]])