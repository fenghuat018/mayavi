#!/usr/bin/env python3
import os
import sys

filename = (
    os.environ.get("mapreduce_map_input_file")
    or os.environ.get("map_input_file")
    or "unknown_file"
)

base = filename.split("/")[-1]
display_name = base.replace("__", "/")

count = 0

try:
    for line in sys.stdin:
        count += 1
except Exception:
    pass

print(f"{display_name}\t{count}")
