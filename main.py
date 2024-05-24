import asyncio

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication
import sys
from fast_gui import MainWindow2D, MainWindow3D
from receiver import Receiver
from midi import MIDISender
from processing import Processor
from player import Player

async def connect_bt(device):
    DEVICE_MAC_ADDRESS = "A0:A3:B3:97:7C:D6"
    SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
    CHARACTERISTIC_UUID = "e68da052-33c2-4814-8793-60112fe6570a"
    await device.scan_and_select_device()
    if device.device_address:
        await device.connect()
        await device.start_notifications(SERVICE_UUID, CHARACTERISTIC_UUID)


async def main():
    app = QApplication(sys.argv)

    # Create and show 2D window
    window2d = MainWindow2D()
    window2d.resize(800, 600)
    window2d.show()

    receiver = Receiver()
    # Create and show 3D window
    window3d = MainWindow3D()
    window3d.resize(800, 600)
    window3d.show()
    processor = Processor()
    await processor.add_receiver(receiver)
    await receiver.add_callback(window2d.update_plot)
    await receiver.add_callback(window3d.update_plot)
    await processor.add_callback(window2d.event_triggered)

    midi = MIDISender()
    player = Player(midi)
    await player.add_receiver(receiver)
    await player.add_event_processor(processor)

    await connect_bt(receiver)

    # Start the Qt event loop
    # sys.exit(app.exec_())
    while True:
        QCoreApplication.processEvents()  # Process Qt events
        await asyncio.sleep(0.005)


if __name__ == "__main__":
    asyncio.run(main())
