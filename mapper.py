#!/usr/bin/env python3
import os
import sys

filename = (
    os.environ.get("mapreduce_map_input_file")
    or os.environ.get("map_input_file")
    or "unknown_file"
)

display_name = filename.split("/")[-1].replace("__", "/")

count = 0

for line in sys.stdin.buffer:
    count += 1

print(f"{display_name}\t{count}")
