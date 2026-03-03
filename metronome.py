
class Metronome:
    """
    Shared rhythmic state. All mutations happen in loop_clock (Conductor).
    All other loops READ only. This prevents data races.

    Time is measured in SCAMP beats. session.tempo controls real-world speed.
    Time signature is fixed at 4/4. Only BPM varies (driven by CPU).
    """

    BPM_MIN = 50.0
    BPM_MAX = 82.0

    def __init__(self):
        self.bpm: float = 60.0
        self._target_bpm: float = 60.0
        self.time_sig: int = 4
        self.bar_count: int = 0
        self.beat_in_bar: int = 0       # 0-indexed within current bar

    # ------------------------------------------------------------------
    # Called once per beat by loop_clock
    # ------------------------------------------------------------------
    def tick(self):
        """Advance one beat. Returns (beat_in_bar, is_downbeat)."""
        self.beat_in_bar += 1
        is_downbeat = (self.beat_in_bar % self.time_sig) == 0

        if is_downbeat:
            self.bar_count += 1
            self.beat_in_bar = 0
            # Smooth BPM towards target: max ±2 BPM per bar
            delta = self._target_bpm - self.bpm
            self.bpm += max(-2.0, min(2.0, delta))

        return self.beat_in_bar, is_downbeat

    # ------------------------------------------------------------------
    # Called by loop_sensor_update
    # ------------------------------------------------------------------
    def update_targets(self, cpu: float, ram: float, net: float):
        # BPM from CPU only; time signature is fixed at 4/4
        self._target_bpm = self.BPM_MIN + cpu * (self.BPM_MAX - self.BPM_MIN)

    def sig_label(self) -> str:
        return "4/4"
