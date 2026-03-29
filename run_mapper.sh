#!/bin/sh
set -eux

echo "=== mapper wrapper debug ===" >&2
echo "PWD=$(pwd)" >&2
echo "--- ls -l ---" >&2
ls -l >&2 || true
echo "--- which python3 ---" >&2
which python3 >&2 || true
echo "--- /usr/bin/python3 --version ---" >&2
/usr/bin/python3 --version >&2 || true
echo "--- mapper.py exists? ---" >&2
ls -l mapper.py >&2 || true
echo "--- reducer.py exists? ---" >&2
ls -l reducer.py >&2 || true

exec /usr/bin/python3 mapper.py
