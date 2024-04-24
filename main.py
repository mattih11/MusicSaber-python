import asyncio
import timeit

from data import SensorDataDecoder
from gui import Gui
from receiver import Receiver
from midi import MIDISender
from timeit import default_timer as timer

async def main():
    DEVICE_MAC_ADDRESS = "A0:A3:B3:97:7C:D6"
    SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
    CHARACTERISTIC_UUID = "e68da052-33c2-4814-8793-60112fe6570a"

    device = Receiver(DEVICE_MAC_ADDRESS)
    gui = Gui()
    midi = MIDISender()
    await device.connect()
    await device.start_notifications(SERVICE_UUID, CHARACTERISTIC_UUID)

    async def my_callback(data):
        received = timer()
        #print("data received: ", received)
        decoded_data = SensorDataDecoder.decode_data(data)
        #print("Received data:", decoded_data)
        mag = SensorDataDecoder.convert_magnetometer_data(decoded_data, "LSM303_MAGGAIN_4_0")
        #print(mag)
        orientation_angles = SensorDataDecoder.calculate_orientation_angles_xyz(mag)
        acc = SensorDataDecoder.convert_accelerometer_data(decoded_data)
        #print(acc)
        gyr = SensorDataDecoder.convert_gyro_data(decoded_data)
        print(gyr)
        converted = timer()
        print("converted: ", converted-received)
        #print(orientation_angles)
        scale_val = orientation_angles['yz'] / 360.0 * 12
        if my_callback.chord is not None:
            midi.stop_notes(my_callback.chord)
            my_callback.chord = None

        if(gyr['x'] > 50):
            my_callback.chord = \
                [midi.c_scale[max(0, round(scale_val) % len(midi.c_scale))],
                 midi.c_scale[max(0, round(scale_val+4) % len(midi.c_scale))],
                 midi.c_scale[max(0, round(scale_val+7) % len(midi.c_scale))]]
            midi.start_notes(my_callback.chord)
        elif(gyr['y'] > 50):
            my_callback.chord = \
                [midi.c_scale[max(0, round(scale_val) % len(midi.c_scale))] + 12,
                 midi.c_scale[max(0, round(scale_val+5) % len(midi.c_scale))] + 12,
                 midi.c_scale[max(0, round(scale_val+9) % len(midi.c_scale))] + 12]
            midi.start_notes(my_callback.chord)
        elif(gyr['x'] < -50):
            my_callback.chord = \
                [midi.c_scale[max(0, round(scale_val) % len(midi.c_scale))],
                 midi.c_scale[max(0, round(scale_val-3) % len(midi.c_scale))],
                 midi.c_scale[max(0, round(scale_val+4) % len(midi.c_scale))]]
            midi.start_notes(my_callback.chord)
        elif(gyr['y'] < -50):
            my_callback.chord = \
                [midi.c_scale[max(0, round(scale_val+4) % len(midi.c_scale))] + 12,
                 midi.c_scale[max(0, round(scale_val+7) % len(midi.c_scale))] + 12,
                 midi.c_scale[max(0, round(scale_val+11) % len(midi.c_scale))] + 12]
            midi.start_notes(my_callback.chord)
        bass = midi.c_scale[max(0, round(scale_val) % len(midi.c_scale))]-24
        if(my_callback.bass != bass):
            if my_callback.bass is not None:
                midi.stop_note(my_callback.bass)
            my_callback.bass = bass
            midi.start_note(bass)

        played = timer()
        print("played: ", played-converted)
        # gui.update(orientation_angles, mag, acc, gyr)
        gui_update = timer()
        print("gui: ", gui_update-played)

    my_callback.chord = None
    my_callback.bass = None
    bass = None
    await device.add_callback(my_callback)

    # Warte auf Benachrichtigungen
    while True:
        await asyncio.sleep(30)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())