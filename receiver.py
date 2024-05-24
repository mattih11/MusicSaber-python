from bleak import BleakClient, BleakScanner
from data import SensorDataDecoder
import time

class Receiver:
    def __init__(self):
        self.client = None
        self.connected = False
        self.callbacks = []

    def __del__(self):
        print("receiver destroyed")
        self.disconnect()

    async def scan_and_select_device(self):
        print("Scanning for devices...")
        devices = await BleakScanner.discover()
        if not devices:
            print("No devices found")
            return None

        print("Found devices:")
        for i, device in enumerate(devices):
            print(f"{i}: {device.name} ({device.address})")

        index = int(input("Enter the number of the device you want to connect to: "))
        self.device_address = devices[index].address

    async def connect(self):
        print("Trying to connect to device with MAC address:", self.device_address)
        if not self.connected:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            self.connected = True
            print("Connected to device with MAC address:", self.device_address)

    async def disconnect(self):
        if self.connected:
            await self.client.disconnect()
            self.connected = False
            print("Disconnected from device with MAC address:", self.device_address)

    async def add_callback(self, callback):
        self.callbacks.append(callback)
        print("Callback added.")

    async def remove_callback(self, callback):
        self.callbacks.remove(callback)
        print("Callback removed.")

    async def handle_data(self, sender, data):
        decoded = SensorDataDecoder.decode_data(data, time.perf_counter())
        for callback in self.callbacks:
            await callback(decoded)
        print("Data handled by callbacks.")

    async def start_notifications(self, service_uuid, characteristic_uuid):
        print("Starting notifications for service UUID:", service_uuid, "and characteristic UUID:", characteristic_uuid)
        await self.client.start_notify(characteristic_uuid, self.handle_data)
        print("Notifications started.")

    async def stop_notifications(self, characteristic_uuid):
        print("Stopping notifications for characteristic UUID:", characteristic_uuid)
        await self.client.stop_notify(characteristic_uuid)
        print("Notifications stopped.")
