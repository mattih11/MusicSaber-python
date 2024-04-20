# LightSaber controlled MIDI device
This repository provides python scripts to receive 9-DoF sensor data via BTLE and generate MIDI signals.
The idea is to generate a device that can translate light saber movements into music.

# TODOs
- add formatter files to the repository
- generate music.py class for musical abstractions, such as harmonies, scales, chords, etc.
- generate analyze.py class to do signal processing and extract events that can trigger midi.
- generate a class that can link events to midi signals (ex. rising edge in signal derivation (neg, pos) --> tigger chord)
- generate calibration.py class to have calibration routines
- generate configuration handling (.yml?)
