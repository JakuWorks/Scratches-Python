"""
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS (USAGE)
- AudD.io AUDIO FILES API KEY!!! (there is a free trial, no card required) 
^ THIS IS OPTIONAL. YOU CAN PASS AN INVALID API KEY TO DISABLE AUDD.IO
- Modern python version!
- shazamio
- requests
REQUIREMENTS (development)
- Modern python version!
- shazamio
- requests
- types-requests
- mypy
- black

IMPORTANT:
Put your songs in a folder called "songs" in the same directory as this script
Then run this script normally and follow the directions

NOTE:
If you don't want to use the (paid) AudD.io api - simply enter an incorrect key.

Date created:
18.02.2025
This is a simple script I wrote to get the sources for a few songs
Also keep in mind that the APIs used are NOT perfect. From my personal results - about 30% of the guesses were incorrect
----------------------------------------------------------------------------------------
"""

import time
import asyncio
import io
from typing import cast, Iterable, Any, Coroutine, TypedDict, Protocol, Union
from pathlib import Path
import shazamio  # type: ignore # Ignore missing stubs
import requests


# SETTINGS
ROOT_DIR: str = "./songs"
AUDD_API_KEY: str = input("Enter your AudD API Key: ")

SHAZAMIO_DELAY: float = 5.0
AUDD_DELAY: float = 5.0

PRINT_METADATA: bool = True
DEBUG_LOGS_ENABLED: bool = True

RESULTS_FILE_NAME: str = r"music_identifier_results.txt"
RESULTS_SEPARATOR: str = " :: "
RESULTS_INFO_PADDING: int = 9


# PROGRAM
class ShazamioHitData(TypedDict):
    title: str
    subtitle: str
    share_subject: str


class AudDHitData(TypedDict):
    artist: str
    title: str
    album: str
    song_link: str


type HitData = Union[ShazamioHitData, AudDHitData]


class Stringable(Protocol):
    def __str__(self) -> str: ...


def debug(message: str, prefix: bool, newline: bool) -> None:
    end: str = "\n" if newline else ""
    beginning: str = "DEBUG | " if prefix else ""
    print(f"{beginning}{message}", end=end)


def pad_string_from_right(string: str, length: int, padding: str = " "):
    to_pad: int = length - len(string)
    padded: str = f"{string}{padding * to_pad}"
    return padded


def warn(message: str) -> None:
    print(f"WARNING | {message}")


def print_metadata_info(songs: Iterable[Path]):
    for song in songs:
        print(song.stat())


def get_shazamio_hits(songs: Iterable[Path]) -> dict[Path, ShazamioHitData]:
    shazam = shazamio.Shazam()
    hits: dict[Path, ShazamioHitData] = {}

    for song in songs:
        debug(f"{song} | Trying with Shazamio...", True, False)
        result_coroutine: Coroutine[Any, Any, dict[str, Any]] = shazam.recognize(
            str(song)
        )
        debug(f" | Awaiting response", False, False)
        result: dict[str, Any] = asyncio.run(result_coroutine)
        debug(f" | Got response", False, False)
        is_hit: bool = "track" in result
        if is_hit:
            debug(f" | HIT", False, False)
            # EDGE CASES WHERE THESE KEYS DON'T EXIST OR DON'T CONTAIN THE PROPER VALUES ARE **NOT** HANDLED!!!
            track = result["track"]
            title = track["title"]
            subtitle = track["subtitle"]
            share_subject = track["share"]["subject"]
            hit: ShazamioHitData = {
                "title": title,
                "subtitle": subtitle,
                "share_subject": share_subject,
            }
            hits[song] = hit
            debug(f" | {hit}", False, False)
        else:
            debug(f" | NOT hit", False, False)
        delay: float = SHAZAMIO_DELAY
        debug(f" | Waiting {delay} seconds", False, False)
        time.sleep(delay)
        debug(f" | Finished", False, True)

    return hits


def get_audd_hits(songs: Iterable[Path]) -> dict[Path, AudDHitData]:
    url: str = r"https://api.audd.io/"
    data: dict[str, str] = {"api_token": AUDD_API_KEY}
    delay: float = AUDD_DELAY

    hits: dict[Path, AudDHitData] = {}

    for song in songs:
        debug(f"{song} Trying with AudD...", True, False)
        with open(song, "rb") as f:
            files: dict[str, io.BufferedReader] = {"file": f}
            debug(f" | Awaiting response", False, False)
            response: requests.Response = requests.post(url=url, data=data, files=files)
            debug(f" | Got Response", False, False)
        parsed: dict[str, Any] = response.json()
        status: str = parsed["status"]

        if status == "error":
            error: dict[str, Any] = parsed["error"]
            code: int = error["error_code"]
            message: str = error["error_message"]
            debug(" | ERROR", False, True)
            warn(
                f"{song} | SKIPPING! | Code: {code} | Visit 'https://docs.audd.io/#common-errors' for error code explanations | Error Message: {message}"
            )

            debug(f"Waiting {delay} seconds", True, False)
            time.sleep(delay)
            debug(f" | Finished", False, True)
            continue

        if status != "success":
            debug(" | ERROR", False, True)
            warn(f"{song} | SKIPPING! | Status: {status} | Unknown status!")

            debug(f"Waiting {delay} seconds", True, True)
            time.sleep(delay)
            debug(f" | Finished", False, True)
            continue

        result: dict[str, Any] | None = parsed["result"]
        if result is not None:
            debug(" | HIT", False, False)
            # EDGE CASES WHERE THESE KEYS DON'T EXIST OR DON'T CONTAIN THE PROPER VALUES ARE **NOT** HANDLED!!!
            artist: str = result["artist"]
            title: str = result["title"]
            album: str = result["album"]
            song_link: str = result["song_link"]
            hit: AudDHitData = {
                "artist": artist,
                "title": title,
                "album": album,
                "song_link": song_link,
            }
            hits[song] = hit
            debug(f" | {hit}", False, False)
        else:
            debug(" | NOT hit", False, False)

        debug(f" | Waiting {delay} seconds", False, False)
        time.sleep(delay)
        debug(f" | Finished", False, True)
    return hits


def save_hits(
    file_name: str,
    hits: dict[Path, HitData],
    leftover_targets: list[Path],
    sep: str,
    padding: int,
) -> None:
    with open(file_name, "wt") as f:
        f.write("< --------------- IDENTIFIED SONGS --------------- >\n")

        for path, hit in hits.items():
            f.write(f"{pad_string_from_right('Path', padding)}{sep}{path}\n")
            for info, value in hit.items():
                f.write(f"{pad_string_from_right(info, padding)}{sep}{value}\n")
            f.write("\n")
        f.write("\n")

        f.write("< --------------- NOT IDENTIFIED SONGS --------------- >\n")
        for path in leftover_targets:
            f.write(f"{str(path)}\n")


def main() -> None:
    root: Path = Path(ROOT_DIR)
    songs: list[Path] = sorted(list(root.iterdir()))

    targets: list[Path] = songs
    hits: dict[Path, HitData] = {}

    selected_files: list[str] = [str(target) for target in targets]
    debug(f"Selected Files: | {' | '.join(selected_files)}", True, True)

    if PRINT_METADATA:
        print("< --------------- METADATA --------------- >", False, True)
        print_metadata_info(targets)
        print("\n")
        # ^ THIS FUNCTION'S INFORMATION IS NOT CONSIDERED A "HIT" HOWEVER IT MAY STILL BE USEFUL

    debug("< --------------- SHAZAM --------------- >", False, True)
    shazamio_hits: dict[Path, HitData] = cast(
        dict[Path, HitData], get_shazamio_hits(targets)
    )

    for path, hit in shazamio_hits.items():
        targets.remove(path)
        hits[path] = hit

    debug("< --------------- AudD --------------- >", False, True)
    audd_hits: dict[Path, HitData] = cast(dict[Path, HitData], get_audd_hits(targets))

    for path, hit in audd_hits.items():
        targets.remove(path)
        hits[path] = hit

    save_hits(RESULTS_FILE_NAME, hits, targets, RESULTS_SEPARATOR, RESULTS_INFO_PADDING)


if __name__ == "__main__":
    main()
