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


def _matches(record: dict[str, Any], where_clause: dict[str, Any]) -> bool:
    """Проверяет, удовлетворяет ли запись всем условиям ``where_clause``."""
    return all(record.get(col) == value for col, value in where_clause.items())


def _is_valid_type(value: Any, col_type: str) -> bool:
    """Проверяет, соответствует ли значение типу столбца из схемы.

    ``bool`` не считается ``int``, хотя в Python является его подклассом.
    """
    match col_type:
        case "int":
            return isinstance(value, int) and not isinstance(value, bool)
        case "str":
            return isinstance(value, str)
        case "bool":
            return isinstance(value, bool)
    return False


def validate_clause(
    metadata: dict[str, Any],
    table_name: str,
    clause: dict[str, Any],
    allow_id: bool = True,
) -> bool:
    """Проверяет, что столбцы условия существуют и значения подходят по типу.

    Args:
        metadata: Текущие метаданные базы данных.
        table_name: Имя существующей таблицы.
        clause: Условие вида ``{столбец: значение}``.
        allow_id: Разрешено ли использовать столбец ``ID`` (запрещено
            для ``set``, так как ID генерируется автоматически).

    Returns:
        ``True``, если условие корректно, иначе ``False``.

    Side effects:
        При ошибке выводит сообщение в stdout.
    """
    columns = metadata[table_name]["columns"]
    for col, value in clause.items():
        if col not in columns or (col == ID_COLUMN and not allow_id):
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return False
        if not _is_valid_type(value, columns[col]):
            print(
                f"Некорректное значение: {value!r} для столбца "
                f"{col}:{columns[col]}. Попробуйте снова."
            )
            return False
    return True


def insert(
    metadata: dict[str, Any],
    table_name: str,
    values: list[Any],
    table_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Добавляет новую запись в таблицу.

    ID записи генерируется автоматически как ``max(ID) + 1``.

    Args:
        metadata: Текущие метаданные базы данных.
        table_name: Имя таблицы.
        values: Значения всех столбцов, кроме ``ID``, в порядке схемы.
        table_data: Текущие записи таблицы.

    Returns:
        Обновлённый список записей. При ошибке (таблицы нет, неверное
        количество или тип значений) данные возвращаются без изменений.

    Side effects:
        Изменяет переданный список ``table_data`` и выводит результат
        операции в stdout.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = [col for col in metadata[table_name]["columns"] if col != ID_COLUMN]
    if len(values) != len(columns):
        print(
            f"Некорректное значение: ожидается {len(columns)} значений "
            f"({', '.join(columns)}), получено {len(values)}. Попробуйте снова."
        )
        return table_data

    record = dict(zip(columns, values))
    if not validate_clause(metadata, table_name, record):
        return table_data

    new_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    table_data.append({ID_COLUMN: new_id, **record})
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(
    table_data: list[dict[str, Any]], where_clause: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Возвращает записи таблицы, удовлетворяющие условию.

    Args:
        table_data: Записи таблицы.
        where_clause: Условие вида ``{столбец: значение}``. Если не задано,
            возвращаются все записи.

    Returns:
        Список подходящих записей.
    """
    if not where_clause:
        return list(table_data)
    return [row for row in table_data if _matches(row, where_clause)]


def update(
    table_data: list[dict[str, Any]],
    set_clause: dict[str, Any],
    where_clause: dict[str, Any],
) -> list[dict[str, Any]]:
    """Обновляет поля записей, удовлетворяющих условию.

    Args:
        table_data: Записи таблицы.
        set_clause: Новые значения вида ``{столбец: значение}``.
        where_clause: Условие отбора записей.

    Returns:
        Изменённый список записей.

    Side effects:
        Изменяет записи в переданном списке ``table_data``.
    """
    for row in table_data:
        if _matches(row, where_clause):
            row.update(set_clause)
    return table_data


def delete(
    table_data: list[dict[str, Any]], where_clause: dict[str, Any]
) -> list[dict[str, Any]]:
    """Удаляет записи, удовлетворяющие условию.

    Args:
        table_data: Записи таблицы.
        where_clause: Условие отбора удаляемых записей.

    Returns:
        Новый список записей без удалённых.
    """
    return [row for row in table_data if not _matches(row, where_clause)]


def table_info(
    metadata: dict[str, Any], table_name: str, table_data: list[dict[str, Any]]
) -> None:
    """Выводит информацию о таблице: имя, столбцы и количество записей.

    Args:
        metadata: Текущие метаданные базы данных.
        table_name: Имя таблицы.
        table_data: Записи таблицы.

    Side effects:
        Печатает информацию в stdout.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    columns = metadata[table_name]["columns"]
    print(f"Таблица: {table_name}")
    print("Столбцы: " + ", ".join(f"{name}:{typ}" for name, typ in columns.items()))
    print(f"Количество записей: {len(table_data)}")
