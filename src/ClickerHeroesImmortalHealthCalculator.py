'''
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS
- Minimum Python 3.8

Date created: 14.10.2024
This is a simple CLI I wrote to calculate the health of an 'immortal' boss in the popular game 'Clicker Heroes'
----------------------------------------------------------------------------------------
'''

# TODO:
# Finish getting the scientific notation for HPs

import time
import math
from typing import Union, Literal


HEALTH_SCIENTIFIC_NOTATION_THRESHOLD = 10 ** 7


def get_scientific_notation_if_above_threshold(number: float, threshold: float, precision: int = 2) -> str:
    if precision < 0:
        raise RuntimeError(f"Precision must be greater than 0! Value: {precision}")

    if number >= threshold:
        format: str = '{:.' + f'{precision}' + 'e}'
        formatted: str = format.format(number)
        return formatted
    
    return str(number)


def get_participation_rate(level: int) -> float:
    # The participation rate on the first 6 immortal levels are 0.1, 0.3, 0.5, 0.2, 0.4, and 0.6. After that, it cycles through 0.3, 0.5, and 0.7.
    unique_rates: list[float] = [0.1, 0.3, 0.5, 0.2, 0.4, 0.6]
    step: int = len(unique_rates)
    participation_rate: float

    if level <= 0:
        participation_rate = 0
    elif level <= step:
        participation_rate = unique_rates[level - 1]
    else:
        levels_above_step: int = level - step

        cycles: list[float] = [0.3, 0.5, 0.7]
        cycles_amount: int = len(cycles)
        cycle: int = (levels_above_step - 1) % cycles_amount
        participation_rate = cycles[cycle]

    return participation_rate

def get_immortal_health(level: int) -> int:
    health_base: int = 17500
    participation_rate: float = get_participation_rate(level)
    modifier: float = 3 ** math.ceil(level / 3)
    health: int = round(health_base * participation_rate * modifier)
    return health

def get_number_difference(first: float, second: float) -> Union[int, float, Literal['infinitely']]:
    if second == 0:
        return 'infinitely'
    else:
        ratio: float = first / second
        difference: float = ratio - 1
        return difference

def get_number_change_text(first: float, second: float, do_round: bool = True, rounding_decimals: int = 0) -> str:
    difference: Union[int, float, Literal['infinitely']]
    word: str

    if first > second:
        difference = get_number_difference(first, second)
        word = 'more'
    elif second > first:
        difference = get_number_difference(second, first)
        word = 'less'
    else:
        difference = 0
        word = 'more'
    
    value: str

    if type(difference) is str and difference == 'infinitely':
        value = difference
    elif type(difference) is int or type(difference) is float:
        percentage: float = difference * 100
        percentage_text: str

        if do_round:
            percentage_rounded: float = round(percentage, rounding_decimals)
            percentage_text = str(percentage_rounded)
        else: 
            percentage_text = str(percentage)

        percentage_text = f'{percentage_text}%'
        value = percentage_text
    else:
        raise RuntimeError(f'Difference type or value is incorrect! Type: {type(difference)}; Value: {difference}')

    text: str = f'{value} {word}'

    return text
    
def get_immortal_health_for_range_message(min: int, max: int) -> str:
    levels: range = range(min, (max + 1))
    health_counts: list[int] = [get_immortal_health(level) for level in levels]
    health_counts_amount: int = len(health_counts)

    messages: list[str] = []

    for current in range(health_counts_amount):
        health: int = health_counts[current]
        health_text: str = get_scientific_notation_if_above_threshold(health, HEALTH_SCIENTIFIC_NOTATION_THRESHOLD, 3)
        level: int = min + current

        message: str = f'Level {level} - {health_text} hp'

        if current > 0:
            previous: int = current - 1
            previous_health: int = health_counts[previous]
            increase: str = get_number_change_text(health, previous_health, rounding_decimals=1)

            message += f' ({increase})'

        messages.append(message)

    all_messages: str = '\n'.join(messages) 
    return all_messages
        
def try_to_int(string: str) -> Union[Literal[False], int]:
    try:
        as_int: int = int(string)
        return as_int
    except ValueError:
        return False

def get_fancy_boundary(boundary_letter: str = '#', boundary_letter_count: int = 15) -> str:
    boundary: str = boundary_letter * boundary_letter_count
    return boundary

def get_fancy_message(string: str, boundary: str = get_fancy_boundary()) -> str:
    fancy_message: str = f'\n{boundary}\n{string}\n{boundary}'
    return fancy_message

def fancy_print(string: str, boundary: str = get_fancy_boundary()) -> None:
    print(get_fancy_message(string, boundary))

def fancy_input(string: str, boundary: str = get_fancy_boundary()) -> str:
    input_value: str = input(f'\n{boundary}\n{string}')
    print(boundary)

    return input_value

def ask_for_level_range() -> tuple[int, int]:
    retry_sleep: float = 0.5

    minimum_level: int
    maximum_level: int

    while True:
        minimum_input: str = fancy_input('You\'re defining the RANGE of immortal boss levels to display HP for. Please enter the MINIMUM level in your range: ')
        minimum_to_int: Union[Literal[False], int] = try_to_int(minimum_input)

        if minimum_to_int is False:
            fancy_print(f'Your input is not an integer!\nRetrying in {retry_sleep} seconds!')
            time.sleep(retry_sleep)
        else:
            minimum_level = minimum_to_int
            break

    while True:
        maximum_input: str = fancy_input('You\'re defining the RANGE of immortal boss levels to display HP for. Please enter the MAXIMUM level in your range: ')
        maximum_to_int: Union[Literal[False], int] = try_to_int(maximum_input)

        if maximum_to_int is False:
            fancy_print(f'Your input is not an integer!\nRetrying in {retry_sleep} seconds!')
            time.sleep(retry_sleep)
        else:
            maximum_level = maximum_to_int
            break

    return (minimum_level, maximum_level)

def interactively_calculate_health_for_immortal_level() -> None:
    fancy_print(f'Calculating the Health of Immortals for a range of levels')

    levels_range: tuple[int, int] = ask_for_level_range()
    
    min: int = levels_range[0]
    max: int = levels_range[1]

    if min > max:
        min, max = max, min

    health_counts: str = get_immortal_health_for_range_message(min, max)
    fancy_print(health_counts)

def main():
    interactively_calculate_health_for_immortal_level()

    repeat_command: str = 'r'
    input_value: str = fancy_input(f"The program ended! Press Enter to exit; or type '{repeat_command}' to repeat it: ")
    
    if input_value == repeat_command:
        main()

main()
