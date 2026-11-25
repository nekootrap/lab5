"""Универсальная сериализация объектов в словарь и обратно.

См. лекцию 5: слайд 13 (сериализация через рефлексию),
слайд 26 (практические примеры сериализации/десериализации).
"""

import dataclasses
import datetime
import types
from typing import Any, Union, get_args, get_origin, get_type_hints

# Имена атрибутов, которые не включаются в результат сериализации.
SKIP_FIELDS: set[str] = {"password"}

_PRIMITIVES = (int, float, str, bool)


def _to_dict_impl(obj: Any, seen: set[int]) -> Any:
    """Внутренняя рекурсивная реализация to_dict с защитой от циклических ссылок."""
    if obj is None or isinstance(obj, _PRIMITIVES):
        return obj

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    if isinstance(obj, (list, tuple, set)):
        return [_to_dict_impl(item, seen) for item in obj]

    if isinstance(obj, dict):
        return {key: _to_dict_impl(value, seen) for key, value in obj.items()}

    if hasattr(obj, "__dict__") and not isinstance(obj, type) and not callable(obj):
        obj_id = id(obj)
        if obj_id in seen:
            return f"<circular: {obj.__class__.__name__}>"

        seen.add(obj_id)
        try:
            result: dict[str, Any] = {"__class__": obj.__class__.__name__}
            # Копируем vars(obj) перед фильтрацией, чтобы не мутировать __dict__ объекта
            for attr, value in dict(vars(obj)).items():
                if attr.startswith("_") or attr in SKIP_FIELDS:
                    continue
                result[attr] = _to_dict_impl(value, seen)
            return result
        finally:
            seen.remove(obj_id)

    raise TypeError(
        f"Неподдерживаемый тип для сериализации: {type(obj).__name__}"
    )


def to_dict(obj: Any) -> Any:
    """Рекурсивно преобразует объект произвольного типа в структуру из примитивов.

    Поддерживаемые случаи:
      - примитивы (int, float, str, bool, None) — возвращаются как есть;
      - datetime.datetime и datetime.date — строка ISO-формата (obj.isoformat());
      - list, tuple, set — список, элементы обрабатываются рекурсивно;
      - dict — словарь, значения обрабатываются рекурсивно;
      - объект произвольного класса — словарь вида
            {"__class__": "<имя класса>", "<атрибут>": <значение>, ...}

    Правила обработки объектов:
      - сериализуются только атрибуты экземпляра (vars(obj));
      - атрибуты, имена которых начинаются с "_", пропускаются;
      - имена из SKIP_FIELDS пропускаются;
      - каждое значение атрибута обрабатывается рекурсивным вызовом to_dict.

    Raises:
        TypeError: если тип obj не входит в перечень поддерживаемых.
    """
    return _to_dict_impl(obj, set())


def _is_optional_or_union(tp: Any) -> bool:
    """Проверяет, является ли аннотация Union или Optional (включая X | Y)."""
    return get_origin(tp) is Union or isinstance(tp, types.UnionType)


def _convert_value(expected_type: Any, value: Any) -> Any:
    """Приводит значение из словаря к ожидаемому типу согласно аннотации."""
    if expected_type is Any:
        return value

    if _is_optional_or_union(expected_type):
        args = get_args(expected_type)
        if value is None and type(None) in args:
            return None
        for option in args:
            if option is type(None):
                continue
            try:
                return _convert_value(option, value)
            except (TypeError, KeyError):
                continue
        raise TypeError(
            f"Значение {value!r} не соответствует ни одному из типов {args}"
        )

    if expected_type is datetime.datetime:
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value)
            except ValueError as exc:
                raise TypeError(
                    f"Некорректный ISO-формат datetime: {value!r}"
                ) from exc
        raise TypeError(
            f"Ожидалась строка ISO-формата для datetime, получен {type(value).__name__}"
        )

    if expected_type is datetime.date:
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.date.fromisoformat(value)
            except ValueError as exc:
                raise TypeError(
                    f"Некорректный ISO-формат date: {value!r}"
                ) from exc
        raise TypeError(
            f"Ожидалась строка ISO-формата для date, получен {type(value).__name__}"
        )

    if expected_type is bool:
        if not isinstance(value, bool):
            raise TypeError(f"Ожидался bool, получен {type(value).__name__}")
        return value

    if expected_type is int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"Ожидался int, получен {type(value).__name__}")
        return value

    if expected_type is float:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"Ожидался float, получен {type(value).__name__}")
        return float(value)

    if expected_type is str:
        if not isinstance(value, str):
            raise TypeError(f"Ожидался str, получен {type(value).__name__}")
        return value

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is list or expected_type is list:
        if not isinstance(value, list):
            raise TypeError(f"Ожидался list, получен {type(value).__name__}")
        if args:
            elem_type = args[0]
            return [_convert_value(elem_type, item) for item in value]
        result_list: list[Any] = []
        for item in value:
            if isinstance(item, dict) and "__class__" in item:
                from python.registry import get_class

                try:
                    item_cls = get_class(item["__class__"])
                    result_list.append(from_dict(item_cls, item))
                    continue
                except (KeyError, NotImplementedError):
                    pass
            result_list.append(item)
        return result_list

    if origin is dict or expected_type is dict:
        if not isinstance(value, dict):
            raise TypeError(f"Ожидался dict, получен {type(value).__name__}")
        if len(args) == 2:
            k_type, v_type = args
            return {
                _convert_value(k_type, k): _convert_value(v_type, v)
                for k, v in value.items()
            }
        return dict(value)

    if isinstance(expected_type, type):
        if isinstance(value, expected_type):
            return value
        if isinstance(value, dict):
            target_cls = expected_type
            if "__class__" in value and value["__class__"] != expected_type.__name__:
                from python.registry import get_class

                try:
                    candidate = get_class(value["__class__"])
                    if issubclass(candidate, expected_type):
                        target_cls = candidate
                except (KeyError, NotImplementedError):
                    pass
            return from_dict(target_cls, value)
        raise TypeError(
            f"Ожидался словарь для {expected_type.__name__}, получен {type(value).__name__}"
        )

    raise TypeError(f"Неподдерживаемая аннотация типа: {expected_type!r}")


def _required_field_names(cls: type, hints: dict[str, Any]) -> set[str]:
    """Определяет набор обязательных полей класса (без значений по умолчанию)."""
    if dataclasses.is_dataclass(cls):
        optional = {
            f.name
            for f in dataclasses.fields(cls)
            if f.default is not dataclasses.MISSING
            or f.default_factory is not dataclasses.MISSING
        }
        return {
            name
            for name in hints
            if not name.startswith("_")
            and name not in SKIP_FIELDS
            and name not in optional
        }

    return {
        name
        for name in hints
        if not name.startswith("_") and name not in SKIP_FIELDS
    }


def from_dict(cls: type, data: dict[str, Any]) -> Any:
    """Восстанавливает объект класса cls из словаря, полученного из to_dict.

    Требования:
      - восстановить все атрибуты, описанные аннотациями класса
        (typing.get_type_hints);
      - строку, соответствующую полю datetime, превратить обратно
        в datetime.datetime через datetime.fromisoformat;
      - вложенный объект (аннотация — класс домена) восстановить
        рекурсивным вызовом from_dict;
      - список объектов (аннотация list[...]) восстановить поэлементно;
      - лишние ключи словаря data игнорировать.

    Raises:
        KeyError: если в data отсутствует обязательное поле класса cls.
        TypeError: если значение поля не приводится к ожидаемому типу.
    """
    if not isinstance(data, dict):
        raise TypeError(
            f"Для восстановления {cls.__name__} ожидался dict, получен {type(data).__name__}"
        )

    hints = get_type_hints(cls)
    required = _required_field_names(cls, hints)
    for field_name in required:
        if field_name not in data:
            raise KeyError(
                f"Отсутствует обязательное поле '{field_name}' для класса {cls.__name__}"
            )

    parsed_fields: dict[str, Any] = {}
    for field_name, expected_type in hints.items():
        if field_name.startswith("_") or field_name in SKIP_FIELDS:
            continue
        if field_name not in data:
            continue
        parsed_fields[field_name] = _convert_value(expected_type, data[field_name])

    if dataclasses.is_dataclass(cls) or cls.__init__ is not object.__init__:
        return cls(**parsed_fields)

    obj = cls.__new__(cls)
    for field_name, field_value in parsed_fields.items():
        setattr(obj, field_name, field_value)
    return obj
