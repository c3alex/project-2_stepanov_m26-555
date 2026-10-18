"""Запуск базы данных: основной цикл и разбор команд пользователя."""

import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help() -> None:
    """Выводит справку по доступным командам.

    Side effects:
        Печатает текст справки в stdout.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Запускает основной цикл работы с базой данных.

    На каждой итерации загружает актуальные метаданные из ``db_meta.json``,
    запрашивает команду у пользователя, разбирает её с помощью ``shlex``
    и вызывает соответствующую функцию из ``core``. После успешных
    операций ``create_table`` и ``drop_table`` метаданные сохраняются.

    Side effects:
        Читает ввод из stdin, печатает в stdout, читает и перезаписывает
        файл ``db_meta.json`` в текущей рабочей директории.
        Завершается по команде ``exit``, Ctrl+C или Ctrl+D.
    """
    print("***База данных***")
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)

        try:
            user_input = prompt.string(">>>Введите команду: ", empty=True)
        except (KeyboardInterrupt, EOFError):
            print()
            return

        try:
            args = shlex.split(user_input or "")
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        if not args:
            continue

        command, *params = args
        match command:
            case "create_table":
                if len(params) < 2:
                    print(
                        "Некорректное значение: укажите имя таблицы и хотя бы "
                        "один столбец. Попробуйте снова."
                    )
                    continue
                table_name, *columns = params
                existed = table_name in metadata
                metadata = create_table(metadata, table_name, columns)
                if not existed and table_name in metadata:
                    save_metadata(METADATA_FILE, metadata)
            case "drop_table":
                if len(params) != 1:
                    print(
                        "Некорректное значение: укажите одно имя таблицы. "
                        "Попробуйте снова."
                    )
                    continue
                table_name = params[0]
                was_present = table_name in metadata
                metadata = drop_table(metadata, table_name)
                if was_present:
                    save_metadata(METADATA_FILE, metadata)
            case "list_tables":
                list_tables(metadata)
            case "help":
                print_help()
            case "exit":
                return
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
