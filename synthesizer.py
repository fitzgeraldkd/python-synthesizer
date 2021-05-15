import struct
import wave
import waveforms, cfg

# GENERAL FUNCTIONS


def interpolate(
    x1: float, x3: float, y1: float, y2: float, y3: float
) -> float:
    return (y2 - y1) / (y3 - y1) * (x3 - x1) + x1


def note_to_freq(note: str) -> float:
    notes = ["A", "As", "B", "C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs"]
    octave = note[-1]
    note = note[:-1]
    delta = int(notes.index(note)) + (int(octave) - 4) * 12
    return 440 * 2 ** (delta / 12)

def transpose(base, offset):
    return base * 2 ** (offset / 12)

# CLASSES


class Envelope:
    def __init__(self, att=0, dec=0, sus=1, rel=0):
        self.att = att
        self.dec = dec
        self.sus = sus
        self.rel = rel

    def out(self, s: float, dur: float) -> float:
        if s > dur and s < dur + self.rel and self.rel > 0:
            # release
            return interpolate(self.out(dur, dur), 0, dur, s, dur + self.rel)
        elif s >= 0 and s < self.att and self.att > 0:
            # attack
            return interpolate(0, 1, 0, s, self.att)
        elif s >= self.att and s < self.dec + self.att and self.dec > 0:
            # decay
            return interpolate(1, self.sus, self.att, s, self.att + self.dec)
        elif s >= self.att + self.dec and s <= dur:
            # sustain
            return self.sus
        else:
            return 0


class Oscillator:
    def __init__(self, wform=waveforms.Waveform, transpose=0, amp=1, env=Envelope(), fm_oscillator=None, fm_amp=1):
        self.wform = wform
        self.transpose = transpose
        self.amp = amp
        self.env = env
        self.fm_oscillator = fm_oscillator
        self.fm_amp = fm_amp

    def out(self, t: float, freq=440) -> float:
        freq = transpose(freq, self.transpose)
        note_start = 0
        note_dur = 5 * cfg.sps
        note_end = note_start + note_dur
        s = t - note_start
        if t >= note_start and t < note_end:
            return self.wform.out(freq) * self.amp * self.env.out(s, note_dur)
        elif t > note_end and t < note_end + self.env.rel:
            return self.wform.out(freq) * self.amp * self.env.out(s, note_dur)
        else:
            return 0


class Track:
    def __init__(
        self, name: str = "", oscillator=Oscillator(), amp=1, notes=[]
    ):
        pass

    def out(self, t) -> float:
        pass

class Algorithm:
    def __init__(self):
        pass

def process(samples=0):
    if samples == 0:
        samples = cfg.duration * cfg.sps
    oscillators = []
    for id in range(cfg.operator_count):
        if not cfg.operators[id]["enabled"]:
            continue
        if cfg.operators[id]["waveform"].lower() == "sine":
            waveform = waveforms.Sine()
        elif cfg.operators[id]["waveform"].lower() == "square":
            waveform = waveforms.Square()
        elif cfg.operators[id]["waveform"].lower() == "sawtooth":
            waveform = waveforms.Sawtooth()
        elif cfg.operators[id]["waveform"].lower() == "triangle":
            waveform = waveforms.Triangle()
        elif cfg.operators[id]["waveform"].lower() == "random":
            waveform = waveforms.Random()
        else:
            waveform = waveforms.Sine()
            print(cfg.operators[id]["waveform"])
        envelope = Envelope(
            att=cfg.operators[id]["attack"],
            dec=cfg.operators[id]["decay"],
            sus=cfg.operators[id]["sustain"],
            rel=cfg.operators[id]["release"],
        )
        oscillators.append(
            Oscillator(
                wform=waveform,
                transpose=cfg.operators[id]["transpose"],
                amp=cfg.operators[id]["amplitude"],
                env=envelope,
            )
        )
    cfg.stream = [0 for x in range(samples)]
    for oscillator in oscillators:
        for sample in range(samples):
            cfg.stream[sample] += oscillator.out(sample)

    try:
        auto_volume = (
            min(
                32768 / max(cfg.stream),
                -32767 / min(cfg.stream),
                cfg.master_volume,
            )
            / cfg.master_volume
        )
    except ZeroDivisionError:
        auto_volume = 1

    for sample in range(len(cfg.stream)):
        cfg.stream[sample] *= auto_volume
        cfg.stream[sample] *= cfg.master_volume


def record():
    process()

    obj = wave.open("test.wav", "w")
    obj.setnchannels(1)
    obj.setsampwidth(2)
    obj.setframerate(44100)
    for sample in cfg.stream:
        data = struct.pack("h", round(sample))
        obj.writeframesraw(data)
    obj.close()
