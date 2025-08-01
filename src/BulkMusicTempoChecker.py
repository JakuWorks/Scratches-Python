"""
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS (USAGE)
- modern python version!
- numpy
- soundfile
- librosa
REQUIREMENTS (development)
- mypy
- black

IMPORTANT:
Put your songs in a folder called "Songs" in the same directory as this script
Adjust your settings in the # Settings section of this file
Then run this script and wait
The allowed file extensions are: aiff au avr caf flac htk svx mat4 mat5 mpc2k mp3 ogg paf pvf raw rf64 sd2 sds ircam voc w64 wav nist wavex wve xi

Date created:
01.07.2025
This is a simple script I wrote to check the bpm (very approximately) of all the songs in large album I've found
This is a very cpu-heavy process
Also keep in mind that the results aren't perfectly accurate (though I think librosa does a good-enough job)
----------------------------------------------------------------------------------------
"""

# fmt:off

from typing import Any
from types import FrameType
import inspect
import functools
from pathlib import Path
import os
import concurrent.futures
import soundfile as sf # Stubs aren't available # type: ignore
import librosa
import numpy as np


# SETTINGS
SONGS_PATH: Path = Path("./Songs")
OUTPUT_RAW: bool = False
OUTPUT_SORT: bool = True
OUTPUT_SORT_REVERSE: bool = True  # Normal order is lowest->highest
OUTPUT_ONLY_FILENAME_AS_TITLE: bool = False  # Disabling will cause the entire (relative) path to be printed as title
OUTPUT_SONG_TEMPOS_TABLE_SEPARATOR: str = " | "
OUTPUT_SONG_TEMPOS_TABLE_DIVIDER_CHAR: str = "-"
OUTPUT_SONG_TEMPOS_TABLE_DIVIDER_AMOUNT: int = 20
GET_SONG_TEMPOS_MAX_WORKERS: int = 12  # Number of workers to handle the processing
LOG_ENABLED: bool = True
LOGS_SEPARATOR: str = " | "

# PROGRAM
# fmt:on
s: str = LOGS_SEPARATOR
ts: str = OUTPUT_SONG_TEMPOS_TABLE_SEPARATOR

if LOG_ENABLED:

    def log(msg: str) -> None:
        caller: str = get_caller()
        print(f"DEBUG{s}{caller}{s}{msg}")

else:

    def log(msg: str) -> None:
        pass


def get_caller() -> str:
    # Function copied from one of my other projects
    frame: FrameType | None = inspect.currentframe()
    if frame is None:
        raise RuntimeError("Can't get frame")
    this: FrameType | None = frame.f_back
    if this is None:
        raise RuntimeError("Can't get first previous frame")
    previous: FrameType | None = this.f_back
    if previous is None:
        raise RuntimeError("Can't get second previous frame")

    name: str = previous.f_code.co_name
    return name


@functools.lru_cache(maxsize=1, typed=True)
def get_allowed_extensions() -> list[str]:
    # File extensions must always be compared lowercase in this script!
    # I'm quite sure that librosa depends on soundfile. And I think that librosa's and soudfile's supported formats should somewhat overlap
    allowed: list[str] = []
    for extension in sf.available_formats().keys():
        allowed.append(extension.lower())
    return allowed


def is_file_allowed(file: Path) -> bool:
    allowed_extensions: list[str] = get_allowed_extensions()
    for extension in file.suffixes:
        extension = extension[1:].lower()
        if extension in allowed_extensions:
            return True
    return False


def collect_files(path: Path) -> list[Path]:
    log(f"Collecting files{s}{path=}")
    files_p: list[Path] = []
    for root, _, files in os.walk(path):
        root_p: Path = Path(root)
        for file in files:
            file_p: Path = root_p / file
            if not is_file_allowed(file_p):
                continue
            files_p.append(file_p)
    log("Finished collecting files")
    return files_p


def get_tempo(file: Path) -> float:
    log(f"Getting tempo{s}{file=}")
    file_log: str = str(file)
    log(f"Loading{s}{file_log}")
    audio_time_series: np.ndarray[Any, Any]  # librosa doesn't tell us the type
    sample_rate: int | float
    audio_time_series, sample_rate = librosa.load(file)  # type: ignore
    log(f"Getting tempo{s}{file_log}")
    tempo: Any | np.ndarray[Any, Any]
    tempo, _ = librosa.beat.beat_track(y=audio_time_series, sr=sample_rate)  # type: ignore
    log(f"Interpreting tempo{s}{file_log}")
    tempo_f: float = interpret_tempo(tempo)
    log(f"Completed{s}{file_log}")
    return tempo_f


def interpret_tempo(tempo: Any) -> float:
    tempo_candidate: Any
    if isinstance(tempo, np.ndarray):
        if tempo.__len__() > 1:  # Using len() made mypy unsatisfied
            raise RuntimeError("Unhandled case - tempo ndarray longer than one")
        tempo_candidate = tempo[0]
    else:
        tempo_candidate = tempo
    try:
        tempo_f: float = float(tempo_candidate)
    except ValueError:
        raise RuntimeError("Unhandled case - couldn't convert tempo candidate float")
    return tempo_f


def get_song_tempos(files: list[Path]) -> list[tuple[Path, float]]:
    log(f"Getting many song tempos{s}Files amount: {len(files)}")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=GET_SONG_TEMPOS_MAX_WORKERS
    ) as exec:
        tempos: list[float] = list(exec.map(get_tempo, files))
    song_tempos: list[tuple[Path, float]] = list(zip(files, tempos))
    log("Finished getting song tempos")
    return song_tempos


def format_song_tempo(
    song_tempo: tuple[Path, float], tempo_rounding: int, name_as_title: bool
) -> str:
    log(f"Formatting song tempo{s}{song_tempo=}{s}{tempo_rounding=}{s}{name_as_title=}")
    tr: int = tempo_rounding
    name: str
    file: Path = song_tempo[0]
    tempo: float = song_tempo[1]
    if name_as_title:
        name = file.name
    else:
        name = str(file)
    return f"{tempo:.{tr}f}{s}{name}"


def sort_song_tempos(
    song_tempos: list[tuple[Path, float]], reverse: bool
) -> list[tuple[Path, float]]:
    def sortkey(song_tempo: tuple[Path, float]) -> float:
        return song_tempo[1]

    return list(sorted(song_tempos, key=sortkey, reverse=reverse))


def format_song_tempos(
    song_tempos: list[tuple[Path, float]],
    tempo_rounding: int,
    name_as_title: bool,
    separator: str,
) -> str:
    log(
        f"Formatting many song tempos{s}Song tempos amount: {len(song_tempos)}{s}{tempo_rounding=}{s}{name_as_title=}{s}{separator=}"
    )
    formatteds: list[str] = []
    for song_tempo in song_tempos:
        formatted: str = format_song_tempo(
            song_tempo, tempo_rounding=tempo_rounding, name_as_title=name_as_title
        )
        formatteds.append(formatted)
    log("Finished formatting song tempos")
    return separator.join(formatteds)


def print_formatted_song_tempos(song_tempos: str) -> None:
    log("Printing formatted song tempos")
    divider = (
        OUTPUT_SONG_TEMPOS_TABLE_DIVIDER_CHAR * OUTPUT_SONG_TEMPOS_TABLE_DIVIDER_AMOUNT
    )
    header_lines: list[str] = [divider, f"TEMPO{ts}TITLE"]
    footer_lines: list[str] = [divider]
    lines: list[str] = [*header_lines, song_tempos, *footer_lines]
    text: str = "\n".join(lines)
    print(text)


def main() -> None:
    if not OUTPUT_RAW:
        print("Working...")
    log(f"Allowed Extensions Are:{s}{s.join(get_allowed_extensions())}")
    files: list[Path] = collect_files(SONGS_PATH)
    song_tempos: list[tuple[Path, float]] = get_song_tempos(files)
    if OUTPUT_SORT:
        song_tempos = sort_song_tempos(song_tempos, reverse=OUTPUT_SORT_REVERSE)
    formatted: str = format_song_tempos(
        song_tempos,
        tempo_rounding=2,
        name_as_title=OUTPUT_ONLY_FILENAME_AS_TITLE,
        separator="\n",
    )
    if OUTPUT_RAW:
        print(formatted)
    else:
        print_formatted_song_tempos(song_tempos=formatted)


if __name__ == "__main__":
    main()
