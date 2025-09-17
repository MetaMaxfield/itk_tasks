def longest_increasing_subsequence(nums: list[int]) -> int:
    result = 1
    local_result = 1
    i = 1
    while i != len(nums):
        if nums[i] > nums[i - 1]:
            local_result += 1
        else:
            result = max(result, local_result)
            local_result = 1
        i += 1
    return max(result, local_result)


if __name__ == "__main__":
    print(longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18]))
