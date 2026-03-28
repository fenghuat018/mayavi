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

for _ in sys.stdin:
    print(f"{display_name}\t1")
