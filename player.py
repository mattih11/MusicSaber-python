from midi import MIDISender
from data import SensorData
from receiver import Receiver
from processing import Event3, EventType, Processor

class Player:
    data: SensorData
    midi: MIDISender
    def __init__(self, midi: MIDISender):
        self.midi = midi
        self.data = None
        self.active_notes = {}

    async def add_receiver(self, receiver: Receiver):
        await receiver.add_callback(self.new_data)

    async def add_event_processor(self, processor: Processor):
        await processor.add_callback(self.event_triggered)

    async def event_triggered(self, events: [Event3]):
        types=set()
        for e in events:
            types.add(e.type)
        for t in types:
            if t == EventType.THRESHOLD_NEG:
                if t not in self.active_notes.keys():
                    self.active_notes[EventType.THRESHOLD_NEG] = self.midi.start_note(self.midi.c_scale[
                                             round((self.data.rot.y + 100) /
                                                   200 * (len(self.midi.c_scale)-1))])
            if t == EventType.THRESHOLD_POS:
                if t not in self.active_notes.keys():
                    self.active_notes[EventType.THRESHOLD_POS] = self.midi.start_note(self.midi.c_scale[
                                             round((self.data.rot.y + 100) /
                                                   200 * (len(self.midi.c_scale)-1))]-24)
        stop_notes = []
        for k, v in self.active_notes.items():
            if k not in types:
                stop_notes.append(k)
        for k in stop_notes:
            self.midi.stop_note(self.active_notes[k])
            self.active_notes.pop(k)

    async def new_data(self, data: SensorData):
        self.data = data