#!/usr/bin/env python3
import os
import sys

# Hadoop Streaming environment var
filename = (
    os.environ.get("mapreduce_map_input_file")
    or os.environ.get("map_input_file")
    or os.environ.get("mapreduce_input_fileinputformat_inputdir")
    or "unknown_file"
)

for _ in sys.stdin:
    print(f"{filename}\t1")
