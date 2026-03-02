import random
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
        self.scale = [0, 2, 4, 7, 9] # Pentatonic Major
        self.root = 60 # Middle C
        self.running = True
        
        # Shared State
        self.cpu = 0.0
        self.ram = 0.0
        self.net = 0.0

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
            volume = 0.3 + (self.cpu * 0.2) # CPU adds a little intensity
            
            # Construct a chord
            notes = []
            base_note = self.root - 12 # One octave down
            
            # Root
            notes.append(base_note)
            # Fifth
            notes.append(base_note + 7)
            # Tenth (Third up an octave)
            notes.append(base_note + 16)
            
            # Play chord
            self.pad.play_chord(notes, volume, duration, blocking=True)
            # Small gap
            wait(random.uniform(0.5, 2.0))

    def loop_droplets(self):
        """Activity Indicators - Driven by CPU (Density)"""
        while self.running:
            # CPU determines wait time (Inverse relationship)
            # Low CPU: Sparse (wait 1-3s)
            # High CPU: Busy (wait 0.1-0.5s)
            
            wait_time = 0.2 + (1.0 - self.cpu) * 2.5
            wait(wait_time)
            
            # Play a note
            # Net usage affects probability of high notes or "sparkles"
            pitch_offset = random.choice([-5, 0, 2, 4, 7, 9, 12, 14])
            if self.net > 0.2 and random.random() < self.net:
                 pitch_offset += 12 # Octave jump on network activity
            
            pitch = self.get_scale_note(self.root + 12, list(self.scale).index(7) + pitch_offset % 5) # Arbitrary mapping
            pitch = self.root + 12 + random.choice(self.scale)
            
            volume = 0.2 + (self.cpu * 0.4)
            duration = random.uniform(0.5, 1.5)
            
            self.droplets.play_note(pitch, volume, duration)

    def loop_bass(self):
        """Deep foundation - Driven by RAM"""
        while self.running:
            duration = random.uniform(6.0, 10.0)
            wait(random.uniform(0.1, 1.0))
            
            # RAM usage pushes bass lower or adds pedal tone
            pitch = self.root - 24
            if self.ram > 0.8:
                pitch = self.root - 24 - 5 # Drop a fourth on high RAM
                
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
