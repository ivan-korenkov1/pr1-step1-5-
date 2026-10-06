"""Эмулятор командной оболочки UNIX-подобной ОС.

Запуск: python3 src/emulator.py [путь_к_VFS] [путь_к_скрипту]
"""

import base64
import getpass
import io
import posixpath
import socket
import sys
import zipfile

config = {"vfs": None, "script": None}
history = []


class ZipVFS:
    """Виртуальная файловая система: файлы ZIP-архива в памяти."""

    def __init__(self):
        """Создаёт пустую VFS, в которой есть только корень /."""
        self.files = {}
        self.dirs = {"/"}
        self.cwd = "/"

    def load(self, zip_path):
        """Читает ZIP-архив в память, не распаковывая его на диск."""
        with open(zip_path, "rb") as file:
            data = io.BytesIO(file.read())
        files = {}
        dirs = {"/"}
        with zipfile.ZipFile(data) as archive:
            for name in archive.namelist():
                if name.startswith("__MACOSX"):
                    continue
                path = "/" + name.rstrip("/")
                if name.endswith("/"):
                    dirs.add(path)
                else:
                    files[path] = decode(archive.read(name))
                parent = posixpath.dirname(path)
                while parent != "/":
                    dirs.add(parent)
                    parent = posixpath.dirname(parent)
        self.files = files
        self.dirs = dirs
        self.cwd = "/"

    def full_path(self, path):
        """Переводит путь в абсолютный с учётом cwd, ".", ".." и "~"."""
        if path.startswith("~"):
            path = "/" + path[1:]
        full = posixpath.normpath(posixpath.join(self.cwd, path))
        return full.replace("//", "/")

    def ls(self, path):
        """Возвращает содержимое каталога или имя файла."""
        full = self.full_path(path)
        if full in self.files:
            return path
        if full not in self.dirs:
            raise ValueError(f"ls: {path}: Нет такого файла или каталога")
        prefix = full.rstrip("/") + "/"
        names = set()
        for item in list(self.files) + list(self.dirs):
            if item.startswith(prefix) and item != full:
                names.add(item[len(prefix):].split("/")[0])
        return "  ".join(sorted(names))

    def cd(self, path):
        """Делает каталог path текущим."""
        full = self.full_path(path)
        if full in self.files:
            raise ValueError(f"cd: {path}: Не каталог")
        if full not in self.dirs:
            raise ValueError(f"cd: {path}: Нет такого файла или каталога")
        self.cwd = full

    def cat(self, path):
        """Возвращает содержимое файла."""
        full = self.full_path(path)
        if full in self.dirs:
            raise ValueError(f"cat: {path}: Это каталог")
        if full not in self.files:
            raise ValueError(f"cat: {path}: Нет такого файла или каталога")
        return self.files[full].rstrip("\n")


def decode(data):
    """Возвращает текст файла, а для двоичного файла - строку base64."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return base64.b64encode(data).decode("ascii")


vfs = ZipVFS()


def get_prompt():
    """Возвращает приглашение вида user@host:~$ по данным ОС."""
    user = getpass.getuser()
    host = socket.gethostname().split(".")[0]
    path = "~" if vfs.cwd == "/" else "~" + vfs.cwd
    return f"{user}@{host}:{path}$ "


def cmd_ls(args):
    """ls [путь]: содержимое каталога (по умолчанию текущего)."""
    if len(args) > 1:
        raise ValueError("ls: слишком много аргументов")
    path = args[0] if args else "."
    return vfs.ls(path)


def cmd_cd(args):
    """cd [путь]: смена текущего каталога, без аргумента - в корень."""
    if len(args) > 1:
        raise ValueError("cd: слишком много аргументов")
    path = args[0] if args else "/"
    vfs.cd(path)
    return ""


def cmd_cat(args):
    """cat файл...: вывод содержимого одного или нескольких файлов."""
    if not args:
        raise ValueError("cat: отсутствует операнд")
    return "\n".join(vfs.cat(path) for path in args)


def cmd_history():
    """history: пронумерованный список введённых команд."""
    lines = []
    for number, command in enumerate(history, start=1):
        lines.append(f"{number:>5}  {command}")
    return "\n".join(lines)


def act(line):
    """Разбирает строку на команду и аргументы и выполняет её."""
    parts = line.split()
    if not parts:
        return ""
    cmd = parts[0]
    args = parts[1:]
    history.append(" ".join(parts))
    if cmd == "exit":
        sys.exit()
    elif cmd == "conf-dump":
        return "\n".join(f"{key}={value}" for key, value in config.items())
    elif cmd == "ls":
        return cmd_ls(args)
    elif cmd == "cd":
        return cmd_cd(args)
    elif cmd == "cat":
        return cmd_cat(args)
    elif cmd == "history":
        return cmd_history()
    else:
        raise ValueError(f"{cmd}: команда не найдена")


def load_vfs(path):
    """Загружает VFS из ZIP-архива; при ошибке выбрасывает ValueError."""
    try:
        vfs.load(path)
    except FileNotFoundError:
        raise ValueError(f"{path}: файл не найден")
    except zipfile.BadZipFile:
        raise ValueError(f"{path}: не является ZIP-архивом")
    except OSError:
        raise ValueError(f"{path}: не удалось открыть файл")
    return f"VFS загружена из {path}: файлов {len(vfs.files)}"


def run_script(path):
    """Выполняет стартовый скрипт и останавливается на первой ошибке."""
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Ошибка: стартовый скрипт {path} не найден")
        sys.exit(1)
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        print(get_prompt() + line)
        try:
            result = act(line)
        except ValueError as error:
            print(error)
            print("Скрипт остановлен из-за ошибки")
            sys.exit(1)
        if result:
            print(result)


def repl():
    """Читает команды пользователя и печатает результат."""
    while True:
        try:
            line = input(get_prompt())
        except EOFError:
            print()
            break
        try:
            result = act(line)
        except ValueError as error:
            result = str(error)
        if result:
            print(result)


def main():
    """Читает параметры запуска, выполняет скрипт и запускает REPL."""
    args = sys.argv[1:]
    if len(args) > 0:
        config["vfs"] = args[0]
    if len(args) > 1:
        config["script"] = args[1]
    print("[debug] Параметры запуска:")
    for key, value in config.items():
        print(f"[debug]   {key} = {value}")
    if config["vfs"]:
        try:
            print(load_vfs(config["vfs"]))
        except ValueError as error:
            print(f"Ошибка загрузки VFS: {error}")
            sys.exit(1)
    if config["script"]:
        run_script(config["script"])
    repl()


if __name__ == "__main__":
    main()
