import math
import struct
import time

class Vec3:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class SensorData:
    rot: Vec3
    acc: Vec3
    gyro: Vec3
    time: float

    def __init__(self, rot: Vec3, acc: Vec3, gyro: Vec3, t: float) -> object:
        self.rot = rot
        self.acc = acc
        self.gyro = gyro
        self.time = t


class SensorDataDecoder:
    def __init__(self):
        pass

    @staticmethod
    def decode_data(data, t=None) -> SensorData:
        if t is None:
            t=time.perf_counter()
        # old protocol (18 byte) - for downwards compatibility
        # this will be deprecated, as we will move to unified
        # protocol using float values instead of raw sensor measurements
        if len(data) == 18:
            mag_x = SensorDataDecoder._decode_16bit(data[1], data[0])
            mag_y = SensorDataDecoder._decode_16bit(data[3], data[2])
            mag_z = SensorDataDecoder._decode_16bit(data[5], data[4])
            acc_x = SensorDataDecoder._decode_16bit(data[7], data[6])
            acc_y = SensorDataDecoder._decode_16bit(data[9], data[8])
            acc_z = SensorDataDecoder._decode_16bit(data[11], data[10])
            g_x = SensorDataDecoder._decode_16bit(data[13], data[12])
            g_y = SensorDataDecoder._decode_16bit(data[15], data[14])
            g_z = SensorDataDecoder._decode_16bit(data[17], data[16])
            mag = SensorDataDecoder.convert_magnetometer_data(Vec3(mag_x, mag_y, mag_z), "LSM303_MAGGAIN_4_0")
            # print(mag)
            orientation_angles = SensorDataDecoder.calculate_orientation_angles_xyz(mag)
            acc = SensorDataDecoder.convert_accelerometer_data(Vec3(acc_x, acc_y, acc_z))
            # print(acc)
            gyr = SensorDataDecoder.convert_gyro_data(Vec3(g_x, g_y, g_z))
            return SensorData(Vec3(mag_x, mag_y, mag_z), Vec3(acc_x, acc_y, acc_z),
                              Vec3(g_x, g_y, g_z), t)
        # new, unified float-based protocol (36 byte)
        # contains all values in float
        elif len(data) == 36:
            num_floats = len(data) // 4
            format_string = f'{num_floats}f'

            # Unpack the byte array into floats
            float_values = struct.unpack(format_string, data)

            print(float_values)  # Output: (1.0, 2.0)
            return SensorData(Vec3(float_values[0], float_values[1], float_values[2]),
                              Vec3(float_values[3], float_values[4], float_values[5]),
                              Vec3(float_values[6], float_values[7], float_values[8]), t)
        else:
            print("unsupported bt protocol format")

    @staticmethod
    def convert_magnetometer_data(mag: Vec3, gain='LSM303_MAGGAIN_4_0') -> Vec3:
        gain_factors = {
            'LSM303_MAGGAIN_1_3': {'xy': 1100, 'z': 980},
            'LSM303_MAGGAIN_1_9': {'xy': 855, 'z': 760},
            'LSM303_MAGGAIN_2_5': {'xy': 670, 'z': 600},
            'LSM303_MAGGAIN_4_0': {'xy': 450, 'z': 400},
            'LSM303_MAGGAIN_4_7': {'xy': 400, 'z': 355},
            'LSM303_MAGGAIN_5_6': {'xy': 330, 'z': 295},
            'LSM303_MAGGAIN_8_1': {'xy': 230, 'z': 205}
        }

        if gain not in gain_factors:
            raise ValueError("Invalid gain value")

        lsm303Mag_Gauss_LSB_XY = gain_factors[gain]['xy']
        lsm303Mag_Gauss_LSB_Z = gain_factors[gain]['z']

        SENSORS_GAUSS_TO_MICROTESLA = 100  # Beispielwert, kann je nach Anwendung angepasst werden

        magnetic_x = mag.x / lsm303Mag_Gauss_LSB_XY * SENSORS_GAUSS_TO_MICROTESLA
        magnetic_y = mag.y / lsm303Mag_Gauss_LSB_XY * SENSORS_GAUSS_TO_MICROTESLA
        magnetic_z = mag.z / lsm303Mag_Gauss_LSB_Z * SENSORS_GAUSS_TO_MICROTESLA

        return Vec3(magnetic_x, magnetic_y, magnetic_z)

    @staticmethod
    def convert_accelerometer_data(acc: Vec3) -> Vec3:

        lsm303_accel_mg_lsb = 0.001  # 1, 2, 4 or 12 mg per lsb
        sensors_gravity_standard = 9.80665

        acc_x = acc.x * lsm303_accel_mg_lsb * sensors_gravity_standard
        acc_y = acc.y * lsm303_accel_mg_lsb * sensors_gravity_standard
        acc_z = acc.z * lsm303_accel_mg_lsb * sensors_gravity_standard

        return Vec3(acc_x, acc_y, acc_z)

    @staticmethod
    def convert_gyro_data(gyro: Vec3) -> Vec3:

        lsm303_gyr_dps_lsb = 8.75 * 0.001  # 8.75 mdps per lsb

        g_x = gyro.x * lsm303_gyr_dps_lsb
        g_y = gyro.y * lsm303_gyr_dps_lsb
        g_z = gyro.z * lsm303_gyr_dps_lsb

        return Vec3(g_x, g_y, g_z)

    @staticmethod
    def _decode_16bit(most_significant_byte, least_significant_byte):
        # Interpretiere die Bytes als vorzeichenbehaftete 16-Bit-Ganzzahl
        value = (most_significant_byte << 8) | least_significant_byte
        # Überprüfe das Vorzeichenbit und konvertiere es entsprechend, wenn es gesetzt ist
        if value & 0x8000:
            value = -((value ^ 0xFFFF) + 1)
        return value

    @staticmethod
    def calculate_orientation_angles_xyz(mag: Vec3) -> Vec3:
        magnetic_x = mag.x
        magnetic_y = mag.y
        magnetic_z = mag.z

        # Annahme: Inklinationswinkel für Deutschland beträgt etwa 60 Grad
        inclination_angle_deg = 60

        # Umrechnung der Magnetometerdaten in lokales Koordinatensystem
        local_magnetic_x = magnetic_x * math.cos(math.radians(inclination_angle_deg)) + magnetic_z * math.sin(
            math.radians(inclination_angle_deg))
        local_magnetic_y = magnetic_y
        local_magnetic_z = -magnetic_x * math.sin(math.radians(inclination_angle_deg)) + magnetic_z * math.cos(
            math.radians(inclination_angle_deg))

        # Berechnung der Orientierungswinkel im lokalen Koordinatensystem
        angle_xy_rad = math.atan2(local_magnetic_y, local_magnetic_x)
        angle_xy_deg = math.degrees(angle_xy_rad)
        if angle_xy_deg < 0:
            angle_xy_deg += 360

        angle_xz_rad = math.atan2(local_magnetic_z, local_magnetic_x)
        angle_xz_deg = math.degrees(angle_xz_rad)
        if angle_xz_deg < 0:
            angle_xz_deg += 360

        angle_yz_rad = math.atan2(local_magnetic_z, local_magnetic_y)
        angle_yz_deg = math.degrees(angle_yz_rad)
        if angle_yz_deg < 0:
            angle_yz_deg += 360

        return Vec3(angle_xy_deg, angle_xz_deg, angle_yz_deg)
