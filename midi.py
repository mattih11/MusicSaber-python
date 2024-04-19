import pygame.midi
import time


class MIDISender:
    c_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C-Dur-Tonleiter
    active_notes = []
    def __init__(self, output_device_id=None):
        if output_device_id is None:
            print("Verfügbare MIDI-Geräte:")
            for i, device in list_midi_devices():
                print(f"{i}: {device}")

            output_device_id = int(input("Geben Sie die ID des gewünschten MIDI-Outputs ein: "))
        pygame.midi.init()
        self.output_port = pygame.midi.Output(output_device_id)

    def start_note(self, note, velocity=64):
        note_on = [0x90, note, velocity]
        self.output_port.write_short(*note_on)
        self.active_notes.append(note)

    def start_notes(self, notes, velocity=64):
        for note in notes:
            note_on = [0x90, note, velocity]
            self.output_port.write_short(*note_on)
            self.active_notes.append(note)

    def stop_note(self, note):
        note_off = [0x80, note, 0]
        self.output_port.write_short(*note_off)
        self.active_notes.remove(note)

    def stop_notes(self, notes):
        for note in notes:
            note_off = [0x80, note, 0]
            self.output_port.write_short(*note_off)
            self.active_notes.remove(note)

    def stop_all(self):
        self.stop_notes(self.active_notes)

    def play_scale(self):
        notes = self.c_scale  # C-Dur-Tonleiter
        for note in notes:
            self.start_note(note)
            time.sleep(0.5)  # Kurze Pause zwischen den Noten
            self.stop_note(note)

    def play_chord(self):
        notes = [60, 64, 67]  # C-Dur-Akkord
        for note in notes:
            self.start_note(note)

        time.sleep(1)  # Dauer des Akkords
        for note in notes:
            self.stop_note(note)

    def play_melody(self):
        melody = [(60, 0.5), (62, 0.5), (64, 0.5), (65, 0.5)]  # Einfache Melodie
        for note, duration in melody:
            self.start_note(note)
            time.sleep(duration)
            self.stop_note(note)

    def close(self):
        del self.output_port
        pygame.midi.quit()


def list_midi_devices():
    pygame.midi.init()
    devices = []
    for i in range(pygame.midi.get_count()):
        device_info = pygame.midi.get_device_info(i)
        device_name = device_info[1].decode('utf-8')
        devices.append((i, device_name))
    pygame.midi.quit()
    return devices


def main():
    midi_sender = MIDISender()
    midi_sender.play_scale()
    midi_sender.play_chord()
    midi_sender.play_melody()
    midi_sender.close()


if __name__ == "__main__":
    main()
