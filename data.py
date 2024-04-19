import math

class SensorDataDecoder:
    def __init__(self):
        pass

    @staticmethod
    def decode_data(data):
        mag_x = SensorDataDecoder._decode_16bit(data[1], data[0])
        mag_y = SensorDataDecoder._decode_16bit(data[3], data[2])
        mag_z = SensorDataDecoder._decode_16bit(data[5], data[4])
        acc_x = SensorDataDecoder._decode_16bit(data[7], data[6])
        acc_y = SensorDataDecoder._decode_16bit(data[9], data[8])
        acc_z = SensorDataDecoder._decode_16bit(data[11], data[10])
        g_x = SensorDataDecoder._decode_16bit(data[13], data[12])
        g_y = SensorDataDecoder._decode_16bit(data[15], data[14])
        g_z = SensorDataDecoder._decode_16bit(data[17], data[16])
        return {
            'mag_x': mag_x,
            'mag_y': mag_y,
            'mag_z': mag_z,
            'acc_x': acc_x,
            'acc_y': acc_y,
            'acc_z': acc_z,
            'g_x': g_x,
            'g_y': g_y,
            'g_z': g_z
        }

    @staticmethod
    def convert_magnetometer_data(raw, gain='LSM303_MAGGAIN_1_3'):
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

        magnetic_x = raw['mag_x'] / lsm303Mag_Gauss_LSB_XY * SENSORS_GAUSS_TO_MICROTESLA
        magnetic_y = raw['mag_y'] / lsm303Mag_Gauss_LSB_XY * SENSORS_GAUSS_TO_MICROTESLA
        magnetic_z = raw['mag_z'] / lsm303Mag_Gauss_LSB_Z * SENSORS_GAUSS_TO_MICROTESLA

        return {'x': magnetic_x, 'y': magnetic_y, 'z': magnetic_z}

    @staticmethod
    def convert_accelerometer_data(raw):

        lsm303Accel_MG_LSB = 0.001   # 1, 2, 4 or 12 mg per lsb
        SENSORS_GRAVITY_STANDARD = 9.80665

        acc_x = raw['acc_x'] * lsm303Accel_MG_LSB * SENSORS_GRAVITY_STANDARD
        acc_y = raw['acc_y'] * lsm303Accel_MG_LSB * SENSORS_GRAVITY_STANDARD
        acc_z = raw['acc_z'] * lsm303Accel_MG_LSB * SENSORS_GRAVITY_STANDARD

        return {'x': acc_x, 'y': acc_y, 'z': acc_z}

    @staticmethod
    def convert_gyro_data(raw):

        lsm303Gyr_DPS_LSB = 8.75 * 0.001   # 8.75 mdps per lsb

        g_x = raw['g_x'] / lsm303Gyr_DPS_LSB
        g_y = raw['g_y'] / lsm303Gyr_DPS_LSB
        g_z = raw['g_z'] / lsm303Gyr_DPS_LSB

        return {'x': g_x, 'y': g_y, 'z': g_z}

    @staticmethod
    def _decode_16bit(most_significant_byte, least_significant_byte):
        # Interpretiere die Bytes als vorzeichenbehaftete 16-Bit-Ganzzahl
        value = (most_significant_byte << 8) | least_significant_byte
        # Überprüfe das Vorzeichenbit und konvertiere es entsprechend, wenn es gesetzt ist
        if value & 0x8000:
            value = -((value ^ 0xFFFF) + 1)
        return value

    @staticmethod
    def calculate_orientation_angles_xyz(magnetic_data):
        magnetic_x = magnetic_data['x']
        magnetic_y = magnetic_data['y']
        magnetic_z = magnetic_data['z']

        # Annahme: Inklinationswinkel für Deutschland beträgt etwa 60 Grad
        inclination_angle_deg = 60

        # Umrechnung der Magnetometerdaten in lokales Koordinatensystem
        local_magnetic_x = magnetic_x * math.cos(math.radians(inclination_angle_deg)) + magnetic_z * math.sin(math.radians(inclination_angle_deg))
        local_magnetic_y = magnetic_y
        local_magnetic_z = -magnetic_x * math.sin(math.radians(inclination_angle_deg)) + magnetic_z * math.cos(math.radians(inclination_angle_deg))

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

        return {'xy': angle_xy_deg, 'xz': angle_xz_deg, 'yz': angle_yz_deg}