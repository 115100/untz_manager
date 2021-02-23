"""Implementation of collections of music files"""
from typing import Iterator
import glob
import os
import re
import subprocess
import tempfile


class Directory:
    def __init__(self, directory: str):
        if not os.path.isdir(directory):
            raise ValueError("{} is not a directory".format(directory))
        self.directory = directory

    def __iter__(self) -> Iterator[str]:
        return glob.iglob(f"{self.directory}/**/*.flac", recursive=True)


class Cue:
    def __init__(self, cue_path: str):
        # We rely on garbage collection to clean this up.
        # An explicit cleanup can also work but makes the code a little messier.
        self._dir = tempfile.TemporaryDirectory()

        # Hacky, but cuetools.sh really doesn't like dos line endings
        unix_cue_path = os.path.join(self._dir.name, os.path.basename(cue_path))
        subprocess.run(
            ["dos2unix", "-n", cue_path, unix_cue_path],
            capture_output=True,
            check=True,
        )

        # shnsplit doesn't handle finding the file for us,
        # so find it from the cue sheet ourselves.
        pattern = re.compile('FILE "(.+)" WAVE')
        audio_path = ""
        with open(unix_cue_path) as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    audio_path = os.path.join(os.path.dirname(cue_path), match.group(1))
        if not audio_path:
            raise FileNotFoundError("Cannot find audio data path")

        subprocess.run(
            [
                "shnsplit",
                "-t",
                "%n - %t",
                "-o",
                "flac",
                "-d",
                self._dir.name,
                "-f",
                unix_cue_path,
                audio_path,
            ],
            capture_output=True,
            check=True,
        )

        subprocess.run(
            [
                "cuetag.sh",
                unix_cue_path,
            ]
            + glob.glob(os.path.join(self._dir.name, "*.flac")),
            capture_output=True,
            check=True,
        )

    def __iter__(self) -> Iterator[str]:
        return glob.iglob(f"{self._dir.name}/*.flac")
