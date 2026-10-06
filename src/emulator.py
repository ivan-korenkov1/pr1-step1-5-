"""Эмулятор командной оболочки UNIX-подобной ОС.

Запуск: python3 src/emulator.py [путь_к_VFS] [путь_к_скрипту]
"""

import getpass
import socket
import sys

config = {"vfs": None, "script": None}


def get_prompt():
    """Возвращает приглашение вида user@host:~$ по данным ОС."""
    user = getpass.getuser()
    host = socket.gethostname().split(".")[0]
    return f"{user}@{host}:~$ "


def act(line):
    """Разбирает строку на команду и аргументы и выполняет её."""
    parts = line.split()
    if not parts:
        return ""
    cmd = parts[0]
    args = parts[1:]
    if cmd == "exit":
        sys.exit()
    elif cmd == "conf-dump":
        return "\n".join(f"{key}={value}" for key, value in config.items())
    elif cmd == "ls":
        return f"ls {args}"
    elif cmd == "cd":
        if len(args) > 1:
            raise ValueError("cd: слишком много аргументов")
        return f"cd {args}"
    else:
        raise ValueError(f"{cmd}: команда не найдена")


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
    if config["script"]:
        run_script(config["script"])
    repl()


if __name__ == "__main__":
    main()
