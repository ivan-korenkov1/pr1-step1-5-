#!/bin/bash
# Этап 5: проверка команд chown и vfs-load и их ошибок.
cd "$(dirname "$0")/.." || exit 1
bash tests/make_zips.sh > /dev/null

echo "=== 1. Стартовый скрипт этапа 5 ==="
python3 src/emulator.py build/deep.zip tests/scripts/stage5.txt

echo "=== 2. vfs-load без начальной VFS ==="
printf "ls\nvfs-load build/minimal.zip\nls -l\nexit\n" > build/one.txt
python3 src/emulator.py "" build/one.txt < /dev/null

echo "=== 3. Ошибки (каждая команда - отдельный запуск) ==="
for command in "chown" "chown alice" "chown : root.txt" \
               "chown alice nope" "vfs-load" "vfs-load a b" \
               "vfs-load build/missing.zip" "vfs-load build/broken.zip"; do
    echo "$command" > build/one.txt
    python3 src/emulator.py build/deep.zip build/one.txt < /dev/null | tail -n 3
done
