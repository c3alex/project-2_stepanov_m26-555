# primitive-db

Примитивная база данных с консольным интерфейсом.

## Установка

```bash
uv build
uv tool install dist/primitive_db-0.1.0-py3-none-any.whl
```

После установки база данных запускается командой:

```bash
database
```

Для разработки можно запускать без установки: `uv run database`.

## Управление таблицами

Метаданные таблиц (имена и структура столбцов) хранятся в файле `db_meta.json`
в текущей директории и сохраняются после каждой успешной операции.

| Команда | Описание |
|---|---|
| `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` | создать таблицу |
| `list_tables` | показать список всех таблиц |
| `drop_table <имя_таблицы>` | удалить таблицу |
| `help` | показать справку |
| `exit` | выйти из программы |

Поддерживаемые типы данных: `int`, `str`, `bool`.
Столбец `ID:int` (уникальный ключ) добавляется в начало таблицы автоматически.

### Пример использования

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: create_table users name:str
Ошибка: Таблица "users" уже существует.

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.

>>>Введите команду: drop_table products
Ошибка: Таблица "products" не существует.

>>>Введите команду: create_table items price:float
Некорректное значение: price:float. Попробуйте снова.

>>>Введите команду: select users
Функции select нет. Попробуйте снова.
```

### Демонстрация

Установка пакета, запуск БД, создание, проверка и удаление таблицы:
[`docs/tables_demo.cast`](docs/tables_demo.cast)
(посмотреть локально: `asciinema play docs/tables_demo.cast`).

<!-- TODO: опубликовать запись (asciinema upload docs/tables_demo.cast) и заменить XXXXXX на её id -->
[![asciicast](https://asciinema.org/a/XXXXXX.svg)](https://asciinema.org/a/XXXXXX)
