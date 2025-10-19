"""
Tablature generation service using librosa for pitch detection
"""
import librosa
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TablatureGenerator:
    """Generate tablatures from separated audio tracks"""

    # Guitar tuning (standard E A D G B E)
    GUITAR_TUNING = {
        'standard': ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
        'drop_d': ['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
        'half_step_down': ['Eb2', 'Ab2', 'Db3', 'Gb3', 'Bb3', 'Eb4']
    }

    # Bass tuning (standard E A D G)
    BASS_TUNING = {
        'standard': ['E1', 'A1', 'D2', 'G2'],
        '5_string': ['B0', 'E1', 'A1', 'D2', 'G2']
    }

    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def hz_to_note(self, frequency: float) -> Tuple[str, int]:
        """
        Convert frequency in Hz to note name and octave
        """
        if frequency <= 0:
            return None, None

        # A4 = 440 Hz
        A4 = 440.0
        note_number = 12 * np.log2(frequency / A4) + 69

        note_idx = int(round(note_number)) % 12
        octave = int(round(note_number) // 12) - 1

        return self.note_names[note_idx], octave

    def note_to_midi(self, note: str, octave: int) -> int:
        """Convert note name and octave to MIDI number"""
        note_base = self.note_names.index(note)
        return (octave + 1) * 12 + note_base

    def extract_pitches(
        self,
        audio_path: str,
        hop_length: int = 512,
        fmin: float = 80.0,
        fmax: float = 1000.0
    ) -> List[Tuple[float, float, float]]:
        """
        Extract pitch information from audio
        Returns list of (time, frequency, confidence)
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)

            # Extract pitches using pYIN algorithm
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=fmin,
                fmax=fmax,
                sr=sr,
                hop_length=hop_length
            )

            # Convert to time series
            times = librosa.frames_to_time(
                np.arange(len(f0)),
                sr=sr,
                hop_length=hop_length
            )

            # Filter out unvoiced and low confidence detections
            pitches = []
            for t, freq, confidence in zip(times, f0, voiced_probs):
                if not np.isnan(freq) and confidence > 0.5:
                    pitches.append((float(t), float(freq), float(confidence)))

            logger.info(f"Extracted {len(pitches)} pitch points from audio")
            return pitches

        except Exception as e:
            logger.error(f"Pitch extraction failed: {e}")
            return []

    def generate_guitar_tab(
        self,
        audio_path: str,
        tuning: str = 'standard'
    ) -> str:
        """
        Generate guitar tablature
        """
        try:
            # Extract pitches
            pitches = self.extract_pitches(audio_path, fmin=82.0, fmax=1200.0)

            if not pitches:
                return "No notes detected in audio"

            # Get tuning
            tuning_notes = self.GUITAR_TUNING.get(tuning, self.GUITAR_TUNING['standard'])

            # Initialize tab lines (6 strings)
            tab_lines = [f"{note}|" for note in reversed(tuning_notes)]
            current_time = 0.0
            time_step = 0.5  # Half second per column

            # Convert tuning to MIDI
            tuning_midi = []
            for note_str in tuning_notes:
                note = note_str[:-1]
                octave = int(note_str[-1])
                tuning_midi.append(self.note_to_midi(note, octave))

            # Process pitches
            for i in range(0, int(pitches[-1][0] / time_step) + 1):
                window_start = i * time_step
                window_end = (i + 1) * time_step

                # Find pitches in this time window
                window_pitches = [
                    (t, freq, conf) for t, freq, conf in pitches
                    if window_start <= t < window_end
                ]

                if window_pitches:
                    # Use pitch with highest confidence
                    _, freq, _ = max(window_pitches, key=lambda x: x[2])

                    # Convert to note
                    note, octave = self.hz_to_note(freq)
                    if note and octave:
                        midi_note = self.note_to_midi(note, octave)

                        # Find best string and fret
                        best_string = None
                        best_fret = None
                        min_fret = 25

                        for string_idx, string_midi in enumerate(tuning_midi):
                            fret = midi_note - string_midi
                            if 0 <= fret <= 24 and fret < min_fret:
                                min_fret = fret
                                best_string = 5 - string_idx  # Reverse for display
                                best_fret = fret

                        # Add to tab
                        if best_string is not None:
                            for s in range(6):
                                if s == best_string:
                                    tab_lines[s] += f"-{best_fret}-"
                                else:
                                    tab_lines[s] += "---"
                        else:
                            for s in range(6):
                                tab_lines[s] += "---"
                else:
                    # No pitch, add rests
                    for s in range(6):
                        tab_lines[s] += "---"

                # Add spacing every 16 columns
                if (i + 1) % 16 == 0:
                    for s in range(6):
                        tab_lines[s] += "|\n" + tuning_notes[5-s] + "|"

            # Finalize
            for s in range(6):
                tab_lines[s] += "|"

            tablature = "\n".join(tab_lines)

            # Add header
            header = f"Guitar Tablature - {tuning.upper()} Tuning\n"
            header += "=" * 50 + "\n\n"

            return header + tablature

        except Exception as e:
            logger.error(f"Guitar tab generation failed: {e}")
            return f"Error generating tablature: {str(e)}"

    def generate_bass_tab(
        self,
        audio_path: str,
        tuning: str = 'standard'
    ) -> str:
        """
        Generate bass tablature
        """
        try:
            # Extract pitches (lower frequency range for bass)
            pitches = self.extract_pitches(audio_path, fmin=40.0, fmax=400.0)

            if not pitches:
                return "No notes detected in audio"

            # Get tuning
            tuning_notes = self.BASS_TUNING.get(tuning, self.BASS_TUNING['standard'])
            num_strings = len(tuning_notes)

            # Initialize tab lines
            tab_lines = [f"{note}|" for note in reversed(tuning_notes)]
            time_step = 0.5

            # Convert tuning to MIDI
            tuning_midi = []
            for note_str in tuning_notes:
                note = note_str[:-1]
                octave = int(note_str[-1])
                tuning_midi.append(self.note_to_midi(note, octave))

            # Process pitches (similar to guitar)
            for i in range(0, int(pitches[-1][0] / time_step) + 1):
                window_start = i * time_step
                window_end = (i + 1) * time_step

                window_pitches = [
                    (t, freq, conf) for t, freq, conf in pitches
                    if window_start <= t < window_end
                ]

                if window_pitches:
                    _, freq, _ = max(window_pitches, key=lambda x: x[2])
                    note, octave = self.hz_to_note(freq)

                    if note and octave:
                        midi_note = self.note_to_midi(note, octave)

                        best_string = None
                        best_fret = None
                        min_fret = 25

                        for string_idx, string_midi in enumerate(tuning_midi):
                            fret = midi_note - string_midi
                            if 0 <= fret <= 24 and fret < min_fret:
                                min_fret = fret
                                best_string = num_strings - 1 - string_idx
                                best_fret = fret

                        if best_string is not None:
                            for s in range(num_strings):
                                if s == best_string:
                                    tab_lines[s] += f"-{best_fret}-"
                                else:
                                    tab_lines[s] += "---"
                        else:
                            for s in range(num_strings):
                                tab_lines[s] += "---"
                else:
                    for s in range(num_strings):
                        tab_lines[s] += "---"

                if (i + 1) % 16 == 0:
                    for s in range(num_strings):
                        tab_lines[s] += "|\n" + tuning_notes[num_strings-1-s] + "|"

            for s in range(num_strings):
                tab_lines[s] += "|"

            tablature = "\n".join(tab_lines)
            header = f"Bass Tablature - {tuning.upper()} Tuning\n"
            header += "=" * 50 + "\n\n"

            return header + tablature

        except Exception as e:
            logger.error(f"Bass tab generation failed: {e}")
            return f"Error generating tablature: {str(e)}"

    def generate_piano_notation(self, audio_path: str) -> str:
        """
        Generate simplified piano notation
        """
        try:
            pitches = self.extract_pitches(audio_path, fmin=27.5, fmax=4200.0)

            if not pitches:
                return "No notes detected in audio"

            notation = "Piano Notation (Simplified)\n"
            notation += "=" * 50 + "\n\n"
            notation += "Time | Note | Octave\n"
            notation += "-" * 50 + "\n"

            for time, freq, conf in pitches[::10]:  # Sample every 10th note
                note, octave = self.hz_to_note(freq)
                if note and octave:
                    notation += f"{time:6.2f}s | {note:4s} | {octave}\n"

            return notation

        except Exception as e:
            logger.error(f"Piano notation generation failed: {e}")
            return f"Error generating notation: {str(e)}"

    def generate_tablature(
        self,
        audio_path: str,
        instrument_type: str,
        tuning: str = 'standard'
    ) -> str:
        """
        Main tablature generation method
        """
        logger.info(f"Generating {instrument_type} tablature from {audio_path}")

        if instrument_type == 'guitar':
            return self.generate_guitar_tab(audio_path, tuning)
        elif instrument_type == 'bass':
            return self.generate_bass_tab(audio_path, tuning)
        elif instrument_type == 'piano':
            return self.generate_piano_notation(audio_path)
        else:
            return f"Unsupported instrument type: {instrument_type}"


# Global instance
tablature_generator = TablatureGenerator()
