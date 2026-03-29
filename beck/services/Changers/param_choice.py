"""Для зависимых IDataChanger: когда поле-источник ещё не задаёт одиночный выбор."""


def is_scalar_choice(val) -> bool:
    """
    True — пользователь задал одно значение (str или int), по нему можно тянуть зависимые данные.
    False — нет значения, пустая строка, или list/tuple (справочник без выбора).
    """
    if val is None:
        return False
    if isinstance(val, (list, tuple)):
        return False
    if isinstance(val, str) and not val.strip():
        return False
    return isinstance(val, (str, int))
