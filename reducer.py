#!/usr/bin/env python3
import sys

current_file = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        filename, count = line.split("\t", 1)
        count = int(count)
    except ValueError:
        continue

    if filename == current_file:
        current_count += count
    else:
        if current_file is not None:
            print(f'"{current_file}": {current_count}')
        current_file = filename
        current_count = count

if current_file is not None:
    print(f'"{current_file}": {current_count}')
