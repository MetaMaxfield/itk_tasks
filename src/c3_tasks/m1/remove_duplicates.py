def remove_duplicates(nums: list[int]) -> tuple[int, list[int]]:
    i_unique = 0
    for i in range(1, len(nums)):
        if nums[i_unique] != nums[i]:
            i_unique += 1
            nums[i_unique] = nums[i]
    i_unique += 1
    return i_unique, nums[:i_unique]


if __name__ == "__main__":
    print(remove_duplicates([1, 1, 2, 2, 3, 4, 4, 5]))
