"""Useful functions to use."""

import argparse
from multiprocessing import cpu_count
from importlib.metadata import version


def get_args() -> argparse.Namespace:
    """Parse and return arguments."""
    parser = argparse.ArgumentParser(
        description="Convert FLACs and sort into a sensible folder hierarchy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--base",
        dest="base_dir",
        help="base directory to store output files to",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--encoder",
        default="opus",
        dest="encoder",
        choices=["opus", "vorbis"],
        help="encoder to use",
    )
    parser.add_argument(
        "-n",
        "--names",
        default="%n - %t",
        dest="pattern",
        help="produce filenames as this string, with %%g (genre), %%a (artist), %%l (album), %%n (track number), %%t (title), %%d (date)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        dest="quality",
        type=float,
        default=10,
        help="sets vorbis encoding quality to n, between -1 (low) and 10 (high)",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        dest="bitrate",
        type=int,
        default=192,
        help="sets opus target bitrate in kbps",
    )
    parser.add_argument(
        "-r",
        "--replaygain",
        dest="replaygain",
        action="store_true",
        help="apply replaygain tags",
    )
    parser.add_argument(
        "-t",
        "--threads",
        dest="threads",
        type=int,
        default=cpu_count(),
        help="thread pool size to spawn",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="set verbose logging",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version("untz_manager"),
        help="print version and exit",
    )
    parser.add_argument(dest="inputs", help="list of folder/file inputs", nargs="+")

    return parser.parse_args()
