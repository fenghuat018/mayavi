#!/usr/bin/env python3
import sys
import os

print("DEBUG: mapper started", file=sys.stderr)
print("DEBUG: cwd unknown", file=sys.stderr)
print("DEBUG: argv =", sys.argv, file=sys.stderr)
print("DEBUG: python executable OK", file=sys.stderr)

for line in sys.stdin:
    print("ok\t1")
