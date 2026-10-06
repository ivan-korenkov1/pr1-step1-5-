#!/bin/bash
# Этап 2: ошибки при запуске и в стартовом скрипте.
cd "$(dirname "$0")/.." || exit 1
bash tests/make_zips.sh > /dev/null

echo "=== 1. Несуществующий стартовый скрипт ==="
python3 src/emulator.py build/deep.zip tests/scripts/missing.txt
echo "код возврата: $?"

echo "=== 2. Скрипт с ошибкой: остановка на первой ошибке ==="
python3 src/emulator.py build/deep.zip tests/scripts/stage2_error.txt
echo "код возврата: $?"
