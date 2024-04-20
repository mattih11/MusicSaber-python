# LightSaber controlled MIDI device
This repository provides python scripts to receive 9-DoF sensor data via BTLE and generate MIDI signals.
The idea is to generate a device that can translate light saber movements into music.

# Class description
A brief overview over the classes and their functionalities, later should be added to the Wiki, I guess.
## Receiver
Receive and handle the BTLE messages based on the python package bleaker
### Problems
BTLE connection is pretty slow and causes the main latency ~100ms, compared to the rest of about 2ms.
It's still not clear if the sender or receiver is causing this latency.
To solve this, there are two main steps to be performed
- make measurements with other devices to be sure it's not a hardware specific topic
- investigate on ESP32 side (other github project)
- --> if this steps fail, we need to have a look for other BTLE libraries or move from python to a more performant C++ project. But this is definitely for later, as we want to do rapid prototyping
## Main (actually not a class)
Start and runs the main loop. Our entry point to the application

# TODOs
- add formatter files to the repository
- generate music.py class for musical abstractions, such as harmonies, scales, chords, etc.
- generate analyze.py class to do signal processing and extract events that can trigger midi.
- generate a class that can link events to midi signals (ex. rising edge in signal derivation (neg, pos) --> tigger chord)
- generate calibration.py class to have calibration routines
- generate configuration handling (.yml?) --> remove magic numbers
