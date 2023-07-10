from typing import TextIO


def parse_rc(fp: TextIO) -> dict:
    contents = fp.readlines()
    parsed = {}
    for line in contents:
        line = line.strip()
        if len(line) > 0 and line.startswith("#"):
            continue

        line = [val.strip().lower() for val in line.split("=")]
        try:
            parsed[line[0]] = line[1]
        except IndexError:
            pass

    return parsed
