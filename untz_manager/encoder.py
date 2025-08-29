"""Encoding related operations"""

import logging
import os
import re
import subprocess
import threading
from typing import List, Mapping, Set

import taglib


class Encoder:
    def __init__(self, base_dir: str, pattern: List[str], ext: str):
        self.lock = threading.Condition()
        self.logger = logging.getLogger("encoder")
        self.base_dir = base_dir.rstrip("/")
        self.output_dirs: Set[str] = set()
        self.pattern = pattern
        self.ext = ext

    def _get_vorbis_comments(self, audio_file: str) -> Mapping[str, str]:
        macros = (
            ("%g", "GENRE"),
            ("%n", "TRACKNUMBER"),
            ("%t", "TITLE"),
            ("%d", "DATE"),
        )

        oggenc_macros = {}
        with taglib.File(audio_file) as afp:
            self.logger.debug('Tags: "%s".', afp.tags)

            for macro, tag in macros:
                if macro in self.pattern:
                    oggenc_macros[macro] = afp.tags.get(tag, ["(none)"])[0]
            # Artist tag is non-standard, so get the first one that matches
            oggenc_macros["%a"] = (
                afp.tags.get("ALBUM_ARTIST", [])
                or afp.tags.get("ALBUMARTIST", [])
                or afp.tags.get("ALBUM ARTIST", [])
                or afp.tags.get("COMPOSER", [])
                or afp.tags.get("PERFORMER", [])
                or afp.tags.get("ARTIST", [])
                or ["Unknown artist"]
            )[0]
            oggenc_macros["%l"] = afp.tags.get("ALBUM", ["Unknown album"])[0]

        return oggenc_macros

    def encode_file(self, audio_file: str) -> None:
        """Encode a given audio file, storing in a logical manner.

        Args:
            audio_file (str): Path to input audio file.
        """
        oggenc_macros = self._get_vorbis_comments(audio_file)

        # Handle patterns on our side.
        output_filename = f"{self.base_dir}/%a/%l/{self.pattern}.{self.ext}"
        for macro, value in oggenc_macros.items():
            output_filename = output_filename.replace(
                macro, re.sub(r"[\"*/:<>?\\|]", "_", value)
            )
        self.output_dirs.add(os.path.dirname(output_filename))

        with self.lock:
            target_path = os.path.dirname(output_filename)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
                self.logger.debug('Created "%s".', target_path)

        process_args = self._encoder_args(audio_file, output_filename)
        self.logger.debug('Running "%s".', " ".join(process_args))
        subprocess.run(process_args, capture_output=True, check=True)

    def _encoder_args(self, audio_file: str, output_filename: str) -> List[str]:
        raise NotImplementedError

    def apply_gain(self, threads: int) -> None:
        """Run gain tagging on base_dir."""
        for output_dir in self.output_dirs:
            process_args = ["rsgain", "easy", "-m", str(threads), output_dir]
            self.logger.debug('Running "%s".', " ".join(process_args))
            subprocess.run(process_args, capture_output=True, check=True)


class OpusEncoder(Encoder):
    def __init__(self, base_dir: str, pattern: List[str], bitrate: int):
        self.bitrate = bitrate
        super().__init__(base_dir=base_dir, pattern=pattern, ext="opus")

    def _encoder_args(self, audio_file: str, output_filename: str) -> List[str]:
        return [
            "opusenc",
            "--bitrate",
            str(self.bitrate),
            audio_file,
            output_filename,
        ]


class VorbisEncoder(Encoder):
    def __init__(self, base_dir: str, pattern: List[str], quality: float):
        self.quality = quality
        super().__init__(base_dir=base_dir, pattern=pattern, ext="ogg")

    def _encoder_args(self, audio_file: str, output_filename: str) -> List[str]:
        return [
            "oggenc",
            "-q",
            str(self.quality),
            "-o",
            output_filename,
            audio_file,
        ]
