import random
import time
from scamp import Session, wait


class Conductor:
    def __init__(self, sensor):
        self.sensor = sensor
        self.session = Session()

        # Setup Instruments (Soft, Ambient)
        # Using default SoundFont presets if available, or fallback
        try:
            self.pad = self.session.new_part("Electric Piano 1")
            self.droplets = self.session.new_part("Vibraphone")
            self.bass = self.session.new_part("Fretless Bass")
        except:
            # Fallback if specific names fail
            self.pad = self.session.new_part("Piano")
            self.droplets = self.session.new_part("Piano")
            self.bass = self.session.new_part("Piano")

        # Musical Parameters
        self.scale = [0, 2, 4, 7, 9]  # Pentatonic Major
        self.root = 60  # Middle C
        self.running = True

        # Shared State
        self.cpu = 0.0
        self.ram = 0.0
        self.net = 0.0

    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def _midi_to_name(self, midi):
        return f"{self.NOTE_NAMES[midi % 12]}{midi // 12 - 1}"

    def get_scale_note(self, base, offset):
        """Maps an index to a note in the scale."""
        octave = offset // len(self.scale)
        degree = offset % len(self.scale)
        return base + self.scale[degree] + (octave * 12)

    def loop_pad(self):
        """Background Drone/Chords - Driven by RAM (Pitch/Depth)"""
        while self.running:
            # RAM determines the root shift (higher RAM = slightly higher tension/pitch)
            # But kept very stable.

            # Slow chords
            duration = random.uniform(4.0, 8.0)
            volume = 0.3 + (self.cpu * 0.2)  # CPU adds a little intensity

            # Construct a chord
            notes = []
            base_note = self.root - 12  # One octave down

            # Root
            notes.append(base_note)
            # Fifth
            notes.append(base_note + 7)
            # Tenth (Third up an octave)
            notes.append(base_note + 16)

            note_names = [self._midi_to_name(n) for n in notes]
            print(
                f"\n[PAD]  {time.strftime('%H:%M:%S')} | "
                f"音色: Electric Piano | 音高: {note_names} | 力度: {volume:.2f} | "
                f"原因: 环境和弦铺底，CPU越高和弦越响 | "
                f"CPU={self.cpu:.0%} RAM={self.ram:.0%} NET={self.net:.0%}"
            )
            self.pad.play_chord(notes, volume, duration, blocking=True)
            wait(random.uniform(0.5, 2.0))

    def loop_droplets(self):
        """Activity Indicators - Driven by CPU (Density)"""
        while self.running:
            # CPU determines wait time (Inverse relationship)
            # Low CPU: Sparse (wait 1-3s)
            # High CPU: Busy (wait 0.1-0.5s)

            wait_time = 0.2 + (1.0 - self.cpu) * 2.5
            wait(wait_time)

            # Net usage triggers high sparkle notes, CPU drives density
            net_sparkle = self.net > 0.2 and random.random() < self.net
            octave_shift = 24 if net_sparkle else 12
            pitch = self.root + octave_shift + random.choice(self.scale)

            volume = 0.2 + (self.cpu * 0.4)
            duration = random.uniform(0.5, 1.5)

            if net_sparkle:
                reason = f"网络流量触发高频闪光音 (NET={self.net:.0%} > 20%，随机触发)"
            else:
                reason = f"CPU活跃度脉冲 (CPU={self.cpu:.0%}，间隔={wait_time:.1f}s，CPU越高越密集)"

            print(
                f"[DROP] {time.strftime('%H:%M:%S')} | "
                f"音色: Vibraphone | 音高: {self._midi_to_name(pitch)} (MIDI {pitch}) | "
                f"力度: {volume:.2f} | 原因: {reason} | "
                f"CPU={self.cpu:.0%} NET={self.net:.0%}"
            )
            self.droplets.play_note(pitch, volume, duration)

    def loop_bass(self):
        """Deep foundation - Driven by RAM"""
        while self.running:
            duration = random.uniform(6.0, 10.0)
            wait(random.uniform(0.1, 1.0))

            pitch = self.root - 24
            if self.ram > 0.8:
                pitch = self.root - 24 - 5
                reason = f"RAM过高 (RAM={self.ram:.0%} > 80%)，低音下沉四度，加深压迫感"
            else:
                reason = f"常规根音持续 (RAM={self.ram:.0%}，稳定)"

            print(
                f"[BASS] {time.strftime('%H:%M:%S')} | "
                f"音色: Fretless Bass | 音高: {self._midi_to_name(pitch)} (MIDI {pitch}) | "
                f"力度: 0.40 | 原因: {reason} | "
                f"RAM={self.ram:.0%}"
            )
            self.bass.play_note(pitch, 0.4, duration)
            wait(duration - 1.0)

    def loop_sensor_update(self):
        """Updates internal state from sensor"""
        while self.running:
            self.sensor.update()
            self.cpu, self.ram, self.net = self.sensor.get_smoothed_metrics()
            # print(f"CPU: {self.cpu:.2f}, RAM: {self.ram:.2f}, NET: {self.net:.2f}")
            wait(1.0)

    def start(self):
        # Fork processes for polyphony
        self.session.fork(self.loop_sensor_update)
        self.session.fork(self.loop_pad)
        self.session.fork(self.loop_droplets)
        self.session.fork(self.loop_bass)

        # Keep main thread alive
        self.session.wait_forever()
