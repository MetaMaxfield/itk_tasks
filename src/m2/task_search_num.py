list_nums = [1, 2, 3, 45, 356, 569, 600, 705, 923]


def search(number: int) -> bool:
    if not list_nums or not (list_nums[0] <= number <= list_nums[-1]):
        return False

    left = 0
    right = len(list_nums)
    while left <= right:
        i = (right + left) // 2
        if list_nums[i] == number:
            return True

        if list_nums[i] > number:
            right = i - 1
        elif list_nums[i] < number:
            left = i + 1

    return False


if __name__ == "__main__":
    for num in range(-1000, 1001):
        if num in list_nums:
            assert search(num)
        else:
            assert not search(num)
