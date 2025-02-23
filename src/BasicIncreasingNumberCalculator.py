"""
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS
- dateutil
- humanize

Date created: around 2023
THIS IS A SIMPLE CALCULATOR CLI
This script takes in an Increase Per Second and Time (inputted in a flexible human way)
This script returns the final number after the Time passes
The number starts at 0
----------------------------------------------------------------------------------------
"""


from datetime import datetime
from dateutil.parser import parse
from humanize import intword
from time import sleep


if __name__ == '__main__':
    # ips - increase per second

    while True:
        print("")
        ips_text: str = input("Please Input Increase Per Second: ")

        try:
            ips_number: float = float(ips_text)
            break
        except ValueError:
            print("")
            print("===========================>")
            print("This is not a valid number!")
            print("Retrying in 1 second!")
            print("<===========================")
            sleep(1)

    print("")
    print(f"Increase Per Second: {ips_number:,}")

    print("")
    time_text: str = input("Please Input Time: ")

    time_datetime: datetime = parse(time_text)
    time_seconds: int = (time_datetime.second +
                        time_datetime.minute * 60 +
                        time_datetime.hour * 60 * 60)
    print("")
    print(f"Time: {time_seconds:,} seconds")

    sum_number: int | float = ips_number * time_seconds
    sum_number_text: str = intword(sum_number, "%0.3f")

    sum_text_line1: str = "===== ===== ===== ====="
    sum_text_line2: str = f"It's {sum_number_text}!"
    sum_text_line3: str = f"(or {sum_number:,})"
    sum_text_line4: str = f"(or {sum_number})"

    sum_text: str = '\n'.join([sum_text_line1, sum_text_line2, sum_text_line3, sum_text_line4])

    print("")
    print(sum_text)

    input("\nEnd...")
