#!/bin/bash
# Этап 2: запуск эмулятора с разными параметрами командной строки.
cd "$(dirname "$0")/.." || exit 1
bash tests/make_zips.sh > /dev/null

echo "=== 1. Без параметров ==="
printf 'conf-dump\nexit\n' | python3 src/emulator.py

echo "=== 2. Только путь к VFS ==="
printf 'conf-dump\nexit\n' | python3 src/emulator.py build/deep.zip

echo "=== 3. Путь к VFS и стартовый скрипт ==="
python3 src/emulator.py build/deep.zip tests/scripts/stage2.txt
