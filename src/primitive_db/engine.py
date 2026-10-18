"""Запуск базы данных: основной цикл и разбор команд пользователя."""

import re
import shlex
from typing import Any

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_info,
    update,
    validate_clause,
)
from primitive_db.parser import find_keyword, parse_set, parse_values, parse_where
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"

INSERT_RE = re.compile(r"insert\s+into\s+(\w+)\s+values\s*(.*)", re.I | re.S)
SELECT_RE = re.compile(r"select\s+from\s+(\w+)\s*(.*)", re.I | re.S)
UPDATE_RE = re.compile(r"update\s+(\w+)\s+set\s+(.*)", re.I | re.S)
DELETE_RE = re.compile(r"delete\s+from\s+(\w+)\s+where\s+(.*)", re.I | re.S)


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

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
        "- создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _invalid(user_input: str) -> None:
    """Выводит сообщение о некорректной команде."""
    print(f"Некорректное значение: {user_input}. Попробуйте снова.")


def _table_exists(metadata: dict[str, Any], table_name: str) -> bool:
    """Проверяет существование таблицы и печатает ошибку, если её нет."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def print_records(metadata: dict[str, Any], table_name: str, records: list) -> None:
    """Выводит записи таблицы в виде таблицы ``PrettyTable``.

    Side effects:
        Печатает таблицу (или сообщение об отсутствии записей) в stdout.
    """
    if not records:
        print("Записи не найдены.")
        return
    columns = list(metadata[table_name]["columns"])
    table = PrettyTable(columns)
    for record in records:
        table.add_row([record.get(col) for col in columns])
    print(table)


def handle_insert(metadata: dict[str, Any], user_input: str) -> None:
    """Обрабатывает ``insert into <таблица> values (...)``.

    Side effects:
        Перезаписывает ``data/<таблица>.json`` при успешной вставке.
    """
    match = INSERT_RE.fullmatch(user_input)
    if not match:
        _invalid(user_input)
        return
    table_name, values_str = match.groups()
    if not _table_exists(metadata, table_name):
        return
    try:
        values = parse_values(values_str)
    except ValueError as error:
        print(f"Некорректное значение: {error}. Попробуйте снова.")
        return
    table_data = load_table_data(table_name)
    count_before = len(table_data)
    table_data = insert(metadata, table_name, values, table_data)
    if len(table_data) > count_before:
        save_table_data(table_name, table_data)


def handle_select(metadata: dict[str, Any], user_input: str) -> None:
    """Обрабатывает ``select from <таблица> [where <условие>]``.

    Side effects:
        Печатает найденные записи в stdout.
    """
    match = SELECT_RE.fullmatch(user_input)
    if not match:
        _invalid(user_input)
        return
    table_name, rest = match.groups()
    if not _table_exists(metadata, table_name):
        return
    where_clause = None
    if rest:
        where_match = re.fullmatch(r"where\s+(.*)", rest, re.I | re.S)
        if not where_match:
            _invalid(user_input)
            return
        try:
            where_clause = parse_where(where_match.group(1))
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
            return
        if not validate_clause(metadata, table_name, where_clause):
            return
    records = select(load_table_data(table_name), where_clause)
    print_records(metadata, table_name, records)


def handle_update(metadata: dict[str, Any], user_input: str) -> None:
    """Обрабатывает ``update <таблица> set <выражение> where <условие>``.

    Side effects:
        Перезаписывает ``data/<таблица>.json``, если записи были обновлены.
    """
    match = UPDATE_RE.fullmatch(user_input)
    if not match:
        _invalid(user_input)
        return
    table_name, rest = match.groups()
    if not _table_exists(metadata, table_name):
        return
    try:
        where_pos = find_keyword(rest, "where")
        if where_pos == -1:
            _invalid(user_input)
            return
        set_clause = parse_set(rest[:where_pos])
        where_clause = parse_where(rest[where_pos + len("where") :])
    except ValueError as error:
        print(f"Некорректное значение: {error}. Попробуйте снова.")
        return
    if not (
        validate_clause(metadata, table_name, set_clause, allow_id=False)
        and validate_clause(metadata, table_name, where_clause)
    ):
        return
    table_data = load_table_data(table_name)
    matched_ids = [row["ID"] for row in select(table_data, where_clause)]
    if not matched_ids:
        print("Записи по заданному условию не найдены.")
        return
    save_table_data(table_name, update(table_data, set_clause, where_clause))
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


def handle_delete(metadata: dict[str, Any], user_input: str) -> None:
    """Обрабатывает ``delete from <таблица> where <условие>``.

    Side effects:
        Перезаписывает ``data/<таблица>.json``, если записи были удалены.
    """
    match = DELETE_RE.fullmatch(user_input)
    if not match:
        _invalid(user_input)
        return
    table_name, where_str = match.groups()
    if not _table_exists(metadata, table_name):
        return
    try:
        where_clause = parse_where(where_str)
    except ValueError as error:
        print(f"Некорректное значение: {error}. Попробуйте снова.")
        return
    if not validate_clause(metadata, table_name, where_clause):
        return
    table_data = load_table_data(table_name)
    matched_ids = [row["ID"] for row in select(table_data, where_clause)]
    if not matched_ids:
        print("Записи по заданному условию не найдены.")
        return
    save_table_data(table_name, delete(table_data, where_clause))
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def run() -> None:
    """Запускает основной цикл работы с базой данных.

    На каждой итерации загружает актуальные метаданные из ``db_meta.json``,
    запрашивает команду у пользователя и вызывает соответствующую функцию
    из ``core``. Команды управления таблицами разбираются с помощью
    ``shlex``, CRUD-команды — парсером из ``parser`` (кавычки в значениях
    важны, поэтому ``shlex`` для них не используется). После успешных
    операций метаданные и данные таблиц сохраняются.

    Side effects:
        Читает ввод из stdin, печатает в stdout, читает и перезаписывает
        файл ``db_meta.json`` и файлы ``data/<таблица>.json`` в текущей
        рабочей директории.
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

        user_input = (user_input or "").strip()
        command = user_input.split(maxsplit=1)[0].lower() if user_input else ""
        crud_handlers = {
            "insert": handle_insert,
            "select": handle_select,
            "update": handle_update,
            "delete": handle_delete,
        }
        if command in crud_handlers:
            crud_handlers[command](metadata, user_input)
            continue

        try:
            args = shlex.split(user_input)
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
                    delete_table_data(table_name)
            case "list_tables":
                list_tables(metadata)
            case "info":
                if len(params) != 1:
                    print(
                        "Некорректное значение: укажите одно имя таблицы. "
                        "Попробуйте снова."
                    )
                    continue
                table_name = params[0]
                table_info(metadata, table_name, load_table_data(table_name))
            case "help":
                print_help()
            case "exit":
                return
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
