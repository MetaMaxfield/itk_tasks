def rle(s: str) -> str:
    new_s = [
        s[0],
    ]
    i = 1
    count = 1
    while i != len(s):
        if s[i] != new_s[-1]:
            new_s.append(str(count))
            count = 0
            new_s.append(s[i])
        count += 1
        i += 1
    new_s.append(str(count))
    return "".join(new_s)


if __name__ == "__main__":
    print(rle("AAABBCCDDD"))
