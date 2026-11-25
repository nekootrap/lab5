"""Универсальный валидатор объектов по аннотациям типов.

См. лекцию 5: слайд 14 (рефлексия для валидации).
"""

import datetime
import types
from typing import Any, Union, get_args, get_origin, get_type_hints


class ValidationError(Exception):
    """Исключение валидации.

    Атрибуты:
        field: имя поля, не прошедшего проверку (или "" для общей ошибки);
        message: человекочитаемое описание проблемы.
    """

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}" if field else message)


def _type_name(tp: Any) -> str:
    """Возвращает читаемое имя ожидаемого типа."""
    if hasattr(tp, "__name__"):
        return tp.__name__
    return str(tp)


def _has_type_hints(cls: type) -> bool:
    """Проверяет, есть ли у класса собственные аннотации типов."""
    try:
        return bool(get_type_hints(cls))
    except Exception:
        return False


def _validate_value(
    cls_name: str,
    field_name: str,
    value: Any,
    expected_type: Any,
    errors: list[str],
) -> None:
    """Проверяет одно значение на соответствие ожидаемой аннотации типа."""
    if expected_type is Any:
        return

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is Union or isinstance(expected_type, types.UnionType):
        if value is None and type(None) in args:
            return
        non_none = [t for t in args if t is not type(None)]
        for option in non_none:
            probe: list[str] = []
            _validate_value(cls_name, field_name, value, option, probe)
            if not probe:
                return
        expected_desc = " | ".join(_type_name(t) for t in args)
        errors.append(
            f"{cls_name}.{field_name}: ожидался {expected_desc}, получен {type(value).__name__}"
        )
        return

    if value is None:
        errors.append(
            f"{cls_name}.{field_name}: ожидался {_type_name(expected_type)}, получен NoneType"
        )
        return

    # Нюанс Python: bool является подклассом int, поэтому проверяем строго
    if expected_type is int:
        if not isinstance(value, int) or type(value) is bool:
            errors.append(
                f"{cls_name}.{field_name}: ожидался int, получен {type(value).__name__}"
            )
        return

    if expected_type is bool:
        if type(value) is not bool:
            errors.append(
                f"{cls_name}.{field_name}: ожидался bool, получен {type(value).__name__}"
            )
        return

    if expected_type in (str, float, datetime.datetime, datetime.date):
        if not isinstance(value, expected_type):
            errors.append(
                f"{cls_name}.{field_name}: ожидался {_type_name(expected_type)}, "
                f"получен {type(value).__name__}"
            )
        return

    if origin is list or expected_type is list:
        if not isinstance(value, list):
            errors.append(
                f"{cls_name}.{field_name}: ожидался list, получен {type(value).__name__}"
            )
            return
        for idx, elem in enumerate(value):
            if args:
                _validate_value(cls_name, f"{field_name}[{idx}]", elem, args[0], errors)
            elif hasattr(elem, "__dict__") and _has_type_hints(type(elem)):
                errors.extend(validate(elem))
        return

    if origin is dict or expected_type is dict:
        if not isinstance(value, dict):
            errors.append(
                f"{cls_name}.{field_name}: ожидался dict, получен {type(value).__name__}"
            )
            return
        if len(args) == 2:
            k_type, v_type = args
            for k, v in value.items():
                _validate_value(cls_name, f"{field_name}[key]", k, k_type, errors)
                _validate_value(cls_name, f"{field_name}[{k!r}]", v, v_type, errors)
        return

    if isinstance(expected_type, type):
        if not isinstance(value, expected_type):
            errors.append(
                f"{cls_name}.{field_name}: ожидался {expected_type.__name__}, "
                f"получен {type(value).__name__}"
            )
            return
        if _has_type_hints(expected_type):
            errors.extend(validate(value))
        return


def validate(obj: Any) -> list[str]:
    """Проверяет атрибуты объекта obj на соответствие аннотациям типов.

    Алгоритм:
      - получить аннотации класса: typing.get_type_hints(type(obj));
      - для каждого поля проверить значение на соответствие типу:
          * примитивные типы (int, str, float, bool) — через isinstance
            (bool не принимается за int);
          * None — ошибка для обычных типов;
          * класс домена (Address, Product, User) — рекурсивный вызов validate;
          * list — проверка каждого элемента;
      - все найденные ошибки собираются в один список.

    Возвращает:
        список сообщений об ошибках; пустой список — объект валиден.
        Формат сообщения: "<ИмяКласса>.<поле>: ожидался <тип>, получен <тип>".
    """
    cls = type(obj)
    cls_name = cls.__name__
    hints = get_type_hints(cls)
    errors: list[str] = []

    for field_name, expected_type in hints.items():
        if not hasattr(obj, field_name):
            errors.append(f"{cls_name}.{field_name}: атрибут отсутствует")
            continue
        value = getattr(obj, field_name)
        _validate_value(cls_name, field_name, value, expected_type, errors)

    return errors


def validate_or_raise(obj: Any) -> None:
    """Выбрасывает ValidationError, если validate(obj) вернул непустой список."""
    errors = validate(obj)
    if errors:
        field = errors[0].split(":", 1)[0] if len(errors) == 1 else ""
        raise ValidationError(field=field, message="; ".join(errors))
