from bleak import BleakClient

class Receiver:
    def __init__(self, device_address):
        self.device_address = device_address
        self.client = None
        self.connected = False
        self.callbacks = []

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
        for callback in self.callbacks:
            await callback(data)
        print("Data handled by callbacks.")

    async def start_notifications(self, service_uuid, characteristic_uuid):
        print("Starting notifications for service UUID:", service_uuid, "and characteristic UUID:", characteristic_uuid)
        await self.client.start_notify(characteristic_uuid, self.handle_data)
        print("Notifications started.")

    async def stop_notifications(self, characteristic_uuid):
        print("Stopping notifications for characteristic UUID:", characteristic_uuid)
        await self.client.stop_notify(characteristic_uuid)
        print("Notifications stopped.")
