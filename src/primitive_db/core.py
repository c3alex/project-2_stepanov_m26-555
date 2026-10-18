"""Основная логика управления таблицами базы данных."""

from typing import Any

VALID_TYPES = ("int", "str", "bool")
ID_COLUMN = "ID"
ID_TYPE = "int"


def _parse_columns(columns: list[str]) -> dict[str, str] | None:
    """Разбирает описания столбцов вида ``имя:тип``.

    Столбец ``ID:int`` добавляется в начало автоматически, если пользователь
    не задал его сам.

    Args:
        columns: Список строк с описаниями столбцов, например ``["age:int"]``.

    Returns:
        Упорядоченный словарь ``{имя_столбца: тип}`` или ``None``, если
        хотя бы одно описание некорректно.

    Side effects:
        При ошибке выводит сообщение о некорректном значении в stdout.
    """
    parsed: dict[str, str] = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, sep, col_type = column.partition(":")
        is_valid = (
            sep == ":"
            and name.isidentifier()
            and col_type in VALID_TYPES
            and (name not in parsed or (name == ID_COLUMN and col_type == ID_TYPE))
        )
        if not is_valid:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        parsed[name] = col_type
    return parsed


def create_table(
    metadata: dict[str, Any], table_name: str, columns: list[str]
) -> dict[str, Any]:
    """Создаёт описание новой таблицы в метаданных.

    Args:
        metadata: Текущие метаданные базы данных.
        table_name: Имя создаваемой таблицы.
        columns: Список столбцов в формате ``имя:тип``. Допустимые типы:
            ``int``, ``str``, ``bool``. Столбец ``ID:int`` добавляется
            в начало автоматически.

    Returns:
        Обновлённый словарь метаданных. Если таблица уже существует или
        столбцы заданы некорректно, метаданные возвращаются без изменений.

    Side effects:
        Изменяет переданный словарь ``metadata`` и выводит результат
        операции в stdout.
    """
    if not table_name.isidentifier():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = _parse_columns(columns)
    if parsed_columns is None:
        return metadata

    metadata[table_name] = {"columns": parsed_columns}
    columns_str = ", ".join(f"{name}:{typ}" for name, typ in parsed_columns.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata


def drop_table(metadata: dict[str, Any], table_name: str) -> dict[str, Any]:
    """Удаляет описание таблицы из метаданных.

    Args:
        metadata: Текущие метаданные базы данных.
        table_name: Имя удаляемой таблицы.

    Returns:
        Обновлённый словарь метаданных. Если таблицы нет, метаданные
        возвращаются без изменений.

    Side effects:
        Изменяет переданный словарь ``metadata`` и выводит результат
        операции в stdout.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict[str, Any]) -> list[str]:
    """Возвращает и выводит список всех таблиц.

    Args:
        metadata: Текущие метаданные базы данных.

    Returns:
        Список имён таблиц в порядке их создания.

    Side effects:
        Выводит имена таблиц в stdout (или сообщение, что таблиц нет).
    """
    tables = list(metadata)
    if not tables:
        print("Таблиц пока нет.")
    for table in tables:
        print(f"- {table}")
    return tables
