"""
Audio separation service using Demucs
"""
import os
import torch
import torchaudio
from pathlib import Path
from typing import Dict, List, Callable, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioSeparator:
    """
    Audio separation using Demucs or Spleeter
    Optimized for Render free tier (limited resources)
    """

    def __init__(self, algorithm: str = "demucs"):
        self.algorithm = algorithm
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initialized AudioSeparator with {algorithm} on {self.device}")

    def separate_demucs(
        self,
        audio_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, str]:
        """
        Separate audio using Demucs
        Returns dict of {instrument_name: file_path}
        """
        try:
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            from demucs.audio import AudioFile

            if progress_callback:
                progress_callback(10.0)

            # Load model (htdemucs for 4 stems: drums, bass, other, vocals)
            model = get_model('htdemucs')
            model.to(self.device)

            if progress_callback:
                progress_callback(30.0)

            # Load audio
            wav = AudioFile(audio_path).read(
                streams=0,
                samplerate=model.samplerate,
                channels=model.audio_channels
            )
            ref = wav.mean(0)
            wav = (wav - ref.mean()) / ref.std()

            if progress_callback:
                progress_callback(50.0)

            # Apply separation
            sources = apply_model(
                model,
                wav[None],
                device=self.device,
                progress=True
            )[0]

            if progress_callback:
                progress_callback(80.0)

            # Save separated sources
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            separated_files = {}
            source_names = model.sources

            for i, source in enumerate(source_names):
                source_path = output_dir / f"{source}.wav"
                source_audio = sources[i] * ref.std() + ref.mean()

                # Save as WAV
                torchaudio.save(
                    str(source_path),
                    source_audio.cpu(),
                    model.samplerate
                )

                separated_files[source] = str(source_path)

            if progress_callback:
                progress_callback(100.0)

            logger.info(f"Successfully separated audio into {len(separated_files)} tracks")
            return separated_files

        except Exception as e:
            logger.error(f"Demucs separation failed: {e}")
            raise

    def separate_spleeter(
        self,
        audio_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, str]:
        """
        Separate audio using Spleeter (fallback)
        Returns dict of {instrument_name: file_path}
        """
        try:
            from spleeter.separator import Separator

            if progress_callback:
                progress_callback(20.0)

            # Initialize Spleeter with 5 stems
            separator = Separator('spleeter:5stems')

            if progress_callback:
                progress_callback(40.0)

            # Perform separation
            output_dir = Path(output_dir)
            separator.separate_to_file(
                audio_path,
                str(output_dir.parent),
                codec='wav'
            )

            if progress_callback:
                progress_callback(80.0)

            # Map Spleeter output files
            audio_name = Path(audio_path).stem
            spleeter_output = output_dir.parent / audio_name

            separated_files = {}
            for stem in ['vocals', 'drums', 'bass', 'piano', 'other']:
                stem_path = spleeter_output / f"{stem}.wav"
                if stem_path.exists():
                    # Move to output directory
                    target_path = output_dir / f"{stem}.wav"
                    stem_path.rename(target_path)
                    separated_files[stem] = str(target_path)

            # Clean up spleeter directory
            if spleeter_output.exists():
                import shutil
                shutil.rmtree(spleeter_output)

            if progress_callback:
                progress_callback(100.0)

            logger.info(f"Successfully separated audio using Spleeter")
            return separated_files

        except Exception as e:
            logger.error(f"Spleeter separation failed: {e}")
            raise

    def separate_audio(
        self,
        audio_path: str,
        output_dir: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, str]:
        """
        Main separation method - chooses algorithm
        """
        logger.info(f"Starting separation of {audio_path} using {self.algorithm}")

        if self.algorithm == "demucs":
            return self.separate_demucs(audio_path, output_dir, progress_callback)
        elif self.algorithm == "spleeter":
            return self.separate_spleeter(audio_path, output_dir, progress_callback)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")


# Global instance
audio_separator = AudioSeparator()
