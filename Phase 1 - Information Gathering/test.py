import re
from functools import reduce


def parse_coords(s: str):
    matches = enumerate(re.findall(r"(\d+(?:\.\d+)?)[°′″]", s))
    val = reduce(lambda acc, val: acc + (float(val[1]) / (60 ** val[0])), matches, 0)
    """
    if len(matches) > 0:
        print("0")
        val += float(matches[0])
    if len(matches) > 1:
        print("1")
        val += float(matches[1]) / 60
    if len(matches) > 2:
        print("2")
        val += float(matches[2]) / 3600
        """
    print(val)


str1 = "45°45′38.59″N"
str2 = "11°12′E"

parse_coords(str1)
parse_coords(str2)
