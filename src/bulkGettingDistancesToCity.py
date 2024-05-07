"""
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS
- geopy
- getmac (used to generate a geopy user agent)

Date created: 22.06.2023
You have a base city. Let's name it A
And a list of other cities. Let's name them Bs
This program will rank Bs by how close they are to A
----------------------------------------------------------------------------------------
"""

from base64 import b64encode
from hashlib import pbkdf2_hmac
from math import sin
from operator import itemgetter
from platform import node, processor
from time import sleep
from datetime import datetime
from typing import Any
from random import randbytes
from base64 import b85encode

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from getmac import get_mac_address


class TooLowWaitTimeError(ValueError):
    pass


def get_current_time_text():
    now: datetime = datetime.now()
    now_text: str = now.strftime(r"%d/%m/%Y,%H:%M:%S:%f")


def compare_strings(str1, str2: str):
    unique_chars: set = set(char for char in str1 + str2)

    str1_char_counts: tuple = tuple((char, str1.count(char)) for char in unique_chars)
    str2_chat_counts: tuple = tuple((char, str2.count(char)) for char in unique_chars)

    return (str1_char_counts == str2_chat_counts and len(str1) == len(str2), str1_char_counts, str2_chat_counts)


def count_cities(my_cities_dict: dict) -> int:
    cites_count: int = 0

    for count_outer_location in my_cities_dict:
        cites_count += len(my_cities_dict[count_outer_location])

    return cites_count


def predictable_shuffle_string(my_string: str, times):
    my_bytearray: bytearray = bytearray(my_string, "utf-8")
    my_bytearray_len: int = len(my_bytearray)
    my_bytearray_len_range: range = range(len(my_bytearray))

    for _ in range(times):
        for character_index_1 in my_bytearray_len_range:
            new_step: int = int(character_index_1 * abs(sin(character_index_1)))
            for character_index_2 in range(0, my_bytearray_len, new_step or 1):
                my_bytearray[character_index_1], my_bytearray[character_index_2] = my_bytearray[character_index_2], my_bytearray[character_index_1]

    return my_bytearray.decode("utf-8")


def get_user_agent_id(anonymous: bool = True, debug: bool = True) -> str:
    # It's still incredibly anonymous no matter what you choose because I don't think anyone is cracking that pbkdf2 anytime soon

    password_foundation_str: str

    if anonymous:
        password_foundation_str = b85encode(randbytes(48)).decode(encoding="utf-8")
    else:
        password_foundation_str = "".join([f"K$92*3x{get_mac_address()}",
                                           f"9k$etv7{get_current_time_text()}s6aV&R2M@7v{node()}",
                                           f"%$85p2{processor()}925RYie".replace(" ", "")])


    password_str: str = predictable_shuffle_string(password_foundation_str, 1)

    if debug:
        print(f"Agent Before Encryption: {password_str}")

    password_bytes: bytes = bytes(password_str, "utf-8")

    salt: bytes = b"\xd7\xc1\x89w\xc09\t\xc5\x8a@X\x01f\x00\xfa\x95"
    times: int = 94558
    id_bytes: bytes = pbkdf2_hmac("sha512", password_bytes, salt, times)

    agent_encrypted: str = b64encode(id_bytes).decode("utf-8")

    if debug:
        print(f"Encrypted Agent: {agent_encrypted}")

    return agent_encrypted


def main() -> None:
    # ================================= CONFIGURATION: =================================

    anonymous: bool = True
    results_decimal_places: int = 2
    wait_seconds: int | float = 1  # Nominatim's Terms of Service do not allow wait \
    # times below 1 second - "No heavy uses (an absolute maximum of 1 request per \
    # second)." - https://operations.osmfoundation.org/policies/nominatim/ 2023.

    city: str = "Gdansk, Poland"

    cities: dict = {r"Poland": (r"Białystok", r"Bielsko-Biała", r"Gniezno", r"Bad City Name Example")}

    min_wait_seconds: int | float = -999  # Disabled. If you break the tos its your fault :)

    # ============================== END OF CONFIGURATION: =============================

    if wait_seconds < min_wait_seconds:
        raise TooLowWaitTimeError(f"Stopped the Script!" f"\nWait Time Below {min_wait_seconds}! ({wait_seconds})!")

    cities_amount: int = count_cities(cities)

    user_agent: str = f"Python_Getting_Distances_Of_{cities_amount}_Cities_To_{city.split(" ")[0].split(",")[0]}_USER_ID_{get_user_agent_id(anonymous=anonymous)}"

    # Nominatim also requires a user_agent name for every Nominatim-using application.
    geolocator: Nominatim = Nominatim(user_agent=user_agent)

    my_city_location: Any = geolocator.geocode(city)

    if not my_city_location:
        print(f"Couldn't get the Location of '{city}'!")
        return

    sleep(wait_seconds)

    my_main_location_coordinates: tuple = (my_city_location.latitude, my_city_location.longitude)

    distances: list = []
    skipped_cities: list = []

    count: int = 0

    for outer_location in cities:
        for city in cities[outer_location]:
            count += 1

            print(f"{count}/{cities_amount}  |  Getting the city {city}", end="")

            city_location = geolocator.geocode(f"{city}, {outer_location}")

            if not city_location:
                skipped_cities.append(f"{city}, {outer_location}")
                print("  |  CITY NOT FOUND!!! | SKIPPED!")
                continue

            city_coordinates: tuple = (city_location.latitude, city_location.longitude)

            distance = geodesic(my_main_location_coordinates, city_coordinates).kilometers
            distances.append((city, distance))

            print(f"  |  Distance - {distance:.{results_decimal_places}f} kilometers")

            sleep(wait_seconds)

    distances.sort(key=itemgetter(1))

    print("\n\n\n\n***************************\nThe sorted distances are: ")

    for i, city_info in enumerate(distances, start=1):
        print(f"{i}. {city_info[0]} - {city_info[1]:.{results_decimal_places}f} " "kilometers")

    print("\nSkipped Cities:")

    for i, skipped_city in enumerate(skipped_cities, start=1):
        print(f"{i}. {skipped_city}")

    print("***************************")


if __name__ == "__main__":
    main()
