#!/bin/bash
# Этап 3: запуск эмулятора с разными вариантами VFS.
cd "$(dirname "$0")/.." || exit 1
bash tests/make_zips.sh

echo "=== 1. Минимальная VFS (один файл) ==="
python3 src/emulator.py build/minimal.zip tests/scripts/stage3.txt

echo "=== 2. VFS с несколькими файлами и двоичным файлом ==="
python3 src/emulator.py build/several.zip tests/scripts/stage3.txt

echo "=== 3. VFS с 3 уровнями вложенности ==="
python3 src/emulator.py build/deep.zip tests/scripts/stage3.txt

echo "=== 4. Несуществующая VFS ==="
python3 src/emulator.py build/missing.zip tests/scripts/stage3.txt
echo "код возврата: $?"

echo "=== 5. Повреждённая VFS ==="
python3 src/emulator.py build/broken.zip tests/scripts/stage3.txt
echo "код возврата: $?"
