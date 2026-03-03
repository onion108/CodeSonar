import bisect
from dataclasses import dataclass
from enum import Enum
import random

@dataclass
class Note:
    name: str
    offset: int
    def __eq__(self, other):
        return self.offset == other.offset
    def __ne__(self, other):
        return self.offset != other.offset
    def __hash__(self):
        return hash(self.offset)

@dataclass
class Chord:
    name: str
    root: int
    intervals: list[int]
    scale: list[int]
    chance: list[float]

    @classmethod
    def major(cls, note: Note) -> 'Chord':
        return Chord(
            note.name + "Maj",
            note.offset,
            [0, 7, 16],
            [0, 2, 4, 5, 7, 9, 11],
            [0.9, 0.1, 0.9, 0.03, 0.9, 0.01, 0.3],
        )
    @classmethod
    def minor(cls, note: Note) -> 'Chord':
        return Chord(
            note.name + "m",
            note.offset,
            [0, 7, 15],
            [0, 2, 3, 5, 7, 8, 10],
            [0.9, 0.1, 0.9, 0.03, 0.9, 0.01, 0.3],
        )

    def pick_note(self):
        """
        Picks a note from the scale.
        The return value will be an offset from the root, so don't forget to add by it.
        """
        whole_prob = sum(self.chance)
        normalized_prob: list[float] = list(map(lambda x: x / whole_prob, self.chance))
        for (i, v) in enumerate(normalized_prob):
            if i == 0:
                continue
            normalized_prob[i] += normalized_prob[i-1]
            pass
        decide = random.random()
        return self.scale[bisect.bisect(normalized_prob, decide)]

@dataclass
class Progression:
    chords: list[Chord]
    next: str | None = None

class Notes:
    C       = Note("C" , 0)
    B_SHARP = Note("B#", 0)
    C_SHARP = Note("C#", 1)
    D_FLAT  = Note("Db", 1)
    D       = Note("D" , 2)
    D_SHARP = Note("D#", 3)
    E_FLAT  = Note("Eb", 3)
    E       = Note("E" , 4)
    F_FLAT  = Note("Fb", 4)
    F       = Note("F" , 5)
    E_SHARP = Note("E#", 5)
    F_SHARP = Note("F#", 6)
    G_FLAT  = Note("Gb", 6)
    G       = Note("G" , 7)
    G_SHARP = Note("G#", 8)
    A_FLAT  = Note("Ab", 8)
    A       = Note("A" , 9)
    A_SHARP = Note("A#", 10)
    B_FLAT  = Note("Bb", 10)
    B       = Note("B" , 11)
    C_FLAT  = Note("Cb", 11)
    
    STANDARD_NAMES = [C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B]

