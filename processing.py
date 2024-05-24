from data import SensorData, Vec3
from enum import Enum
from receiver import Receiver
import time


class Signal3:
    x: [float]
    y: [float]
    z: [float]
    t: [float]

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.t = []

    def append(self, data: Vec3, t: float):
        self.x.append(data.x)
        self.y.append(data.y)
        self.z.append(data.z)
        self.t.append(t)


class History3(Signal3):

    def __init__(self, history_length=20):
        super().__init__()
        self.history_length = history_length

    def append(self, data: Vec3, t: float):
        super().append(data, t)
        # limit data to not overload the RAM
        self.x = self.x[-self.history_length:]
        self.y = self.y[-self.history_length:]
        self.z = self.z[-self.history_length:]
        self.t = self.t[-self.history_length:]


class Derivation3(History3):
    last_data: Vec3

    def __init__(self, history_length=20, absolute=False):
        super().__init__(history_length)
        self.absolute = absolute
        self.last_update = None

    def abs(self, data: float):
        if self.absolute:
            return abs(data)
        else:
            return data

    def append(self, data: Vec3, t: float):
        derive = False
        if self.last_update is not None:
            super().append(Vec3((self.abs(data.x) - self.abs(self.last_data.x)) / (t - self.last_update),
                                (self.abs(data.y) - self.abs(self.last_data.y)) / (t - self.last_update),
                                (self.abs(data.z) - self.abs(self.last_data.z)) / (t - self.last_update)), t)
        self.last_data = data
        self.last_update = t


class SensorHistory:
    rot: History3
    acc: History3
    gyro: History3
    gyro_derivation: Derivation3

    def __init__(self, history_length=20):
        self.rot = History3(history_length)
        self.acc = History3(history_length)
        self.gyro = History3(history_length)
        self.gyro_derivation = Derivation3(history_length)

    def append(self, data: SensorData):
        self.rot.append(data.rot, data.time)
        self.acc.append(data.acc, data.time)
        self.gyro.append(data.gyro, data.time)
        self.gyro_derivation.append(data.gyro, data.time)


class EventType(Enum):
    THRESHOLD_POS = 1,
    THRESHOLD_NEG = 2,
    EDGE_RISE = 3,
    EDGE_FALL = 4


class Dimension(Enum):
    X = 1,
    Y = 2,
    Z = 3


class EventType(Enum):
    THRESHOLD_POS = 1,
    THRESHOLD_NEG = 2,
    EDGE_RISE = 3,
    EDGE_FALL = 4


class Event:
    type: EventType


class Event3:
    type: EventType
    dimension: Dimension

    def __init__(self, position, window_index, value, type: EventType, dimension: Dimension):
        self.position = position
        self.window_index = window_index
        self.value = value
        self.type = type
        self.dimension = dimension


class EventProcessor3:

    def __init__(self, signal: Signal3, window_length=5, cooldown=10,
                 threshold_pos=50, threshold_neg=-50):
        self.signal = signal
        self.window_length = window_length
        self.cooldown = cooldown
        self.threshold_pos = threshold_pos
        self.threshold_neg = threshold_neg

    def analyze(self):
        events = []
        max_threshold_pos = 0
        min_threshold_neg = 0
        for (signal, dimension) in [(self.signal.x, Dimension.X),
                                    (self.signal.y, Dimension.Y),
                                    (self.signal.z, Dimension.Z)]:
            for index, val in enumerate(signal[-self.cooldown:]):
                if val > self.threshold_pos:
                    events.append(Event3(self.signal.t[index-self.cooldown+len(signal)], index,
                                         val, EventType.THRESHOLD_POS, dimension))
                    if val > max_threshold_pos:
                        max_threshold_pos = val
                elif val < self.threshold_neg:
                    events.append(Event3(self.signal.t[index-self.cooldown+len(signal)], index,
                                         val, EventType.THRESHOLD_NEG, dimension))
                    if val < min_threshold_neg:
                        min_threshold_neg = val

            for e in events:
                if e.window_index < self.cooldown - self.window_length:
                    events.remove(e)
                elif e.value < max_threshold_pos and e.type == EventType.THRESHOLD_POS:
                    events.remove(e)
                elif e.value > min_threshold_neg and e.type == EventType.THRESHOLD_NEG:
                    events.remove(e)

        return events


class Processor:
    def __init__(self):
        self.history = SensorHistory()
        self.gyro_dev_processor = EventProcessor3(self.history.gyro_derivation)
        self.callbacks = []
        self.old_nevents = 0

    async def add_receiver(self, receiver: Receiver):
        await receiver.add_callback(self.new_data)

    async def new_data(self, data: SensorData):
        self.history.append(data)
        gyro_deriv_events = self.gyro_dev_processor.analyze()
        if len(gyro_deriv_events) > 0 or self.old_nevents > len(gyro_deriv_events):
            for cb in self.callbacks:
                await cb(gyro_deriv_events)
        self.old_nevents = len(gyro_deriv_events)

    async def add_callback(self, callback):
        self.callbacks.append(callback)

    async def remove_callback(self, callback):
        self.callbacks.remove(callback)