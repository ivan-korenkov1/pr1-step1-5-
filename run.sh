#!/bin/bash
# Запуск эмулятора. Параметры передаются как есть.
cd "$(dirname "$0")" || exit 1
python3 src/emulator.py "$@"
