#!/bin/bash
# Этап 4: проверка команд ls, cd, cat, history и их ошибок.
cd "$(dirname "$0")/.." || exit 1
bash tests/make_zips.sh > /dev/null

echo "=== 1. Стартовый скрипт этапа 4 ==="
python3 src/emulator.py build/deep.zip tests/scripts/stage4.txt

echo "=== 2. Двоичный файл выводится в base64 ==="
printf "cat bin/data.bin\nexit\n" > build/one.txt
python3 src/emulator.py build/several.zip build/one.txt < /dev/null | tail -n 3

echo "=== 3. Ошибки (каждая команда - отдельный запуск) ==="
for command in "ls nope" "ls a b" "cd root.txt" "cd nope" "cd a b" \
               "cat" "cat level1" "cat nope"; do
    echo "$command" > build/one.txt
    python3 src/emulator.py build/deep.zip build/one.txt < /dev/null | tail -n 3
done
