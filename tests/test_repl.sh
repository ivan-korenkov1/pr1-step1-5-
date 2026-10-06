#!/bin/bash
# Этап 1: команды подаются в REPL через канал.
cd "$(dirname "$0")/.." || exit 1
printf '%s\n' "ls" "ls -l /home" "cd docs" "cd a b" "foo" "exit" \
    | python3 src/emulator.py
