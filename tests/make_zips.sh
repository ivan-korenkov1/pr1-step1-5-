#!/bin/bash
# Собирает тестовые ZIP-архивы из папок vfs/ в папку build/.
# Архивы не хранятся в git, поэтому их нужно собрать перед запуском.
cd "$(dirname "$0")/.." || exit 1
mkdir -p build
rm -f build/*.zip

for name in minimal several deep; do
    (cd "vfs/$name" && zip -qr -X "../../build/$name.zip" . -x '.*')
done

# Двоичный файл для проверки base64 добавляется в several.zip.
mkdir -p build/bin
printf '\000\001\002\377\376' > build/bin/data.bin
(cd build && zip -q -X several.zip bin/data.bin)

# Повреждённый архив для проверки ошибок.
echo "это не ZIP-архив" > build/broken.zip

echo "Архивы собраны в папке build/:"
ls build/*.zip
