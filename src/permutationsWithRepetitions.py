"""
----------------------------------------------------------------------------------------
  OVERVIEW

  REQUIREMENTS
  - none

  Date created: around 2023
  This program takes a permutation like [1,2,3,4] and returns its every possible permutation with allowed repetitions.
  In: [1,2,3,4] Out: [1, 1, 1, 1] [1, 1, 1, 2] [1, 1, 1, 3] [1, 1, 1, 4] [1, 1, 2, 1] and so on...
  The input is STATIC!!! You must edit the code to change it!

----------------------------------------------------------------------------------------
"""

from math import ceil


def list_my_list(my_list: list) -> list:
    my_listed_list: list = []

    for item in my_list:
        my_listed_list.append([item])

    return my_listed_list


def get_permutations(my_list: list, size: None | int = None) -> list:
    size = size or len(my_list)

    if size > len(my_list):
        raise ValueError("The value of size passed to the function cannot be greater than the length of the passed list!")

    my_list = list_my_list(my_list)

    def add_one_permutation_depth(current_permutation: list) -> list:
        deeper_permutations: list = []

        for item_to_append in my_list:
            deeper_permutations.append(current_permutation + item_to_append)
        return deeper_permutations

    def recursively_add_one_permutation_depth(current_permutations: list) -> list:
        if len(current_permutations[0]) < size:

            new_permutations: list = []

            for permutation in current_permutations:
                new_permutations += add_one_permutation_depth(permutation)

            return recursively_add_one_permutation_depth(new_permutations)

        return current_permutations

    return recursively_add_one_permutation_depth(my_list)


def example1():
    my_size: int = 4
    my_array: list = [1, 2, 3, 4]

    my_permutations: list = get_permutations(my_array, size=my_size)

    print(f"My Array: {my_array}"
          f"\nThe size of each permutation: {my_size}"
          f"\nPermutations:\n")

    for i in range(1, ceil((len(my_permutations)/my_size) + 1)):
        print(*my_permutations[my_size * (i - 1): my_size * i])

    print(f"\nEnd! - {len(my_permutations)} Permutations!")


if __name__ == '__main__':
    example1()
