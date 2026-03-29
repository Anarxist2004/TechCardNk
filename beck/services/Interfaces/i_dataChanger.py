from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from services.Interfaces.i_servise import IServise
T = TypeVar('T')

class IDataChanger(ABC, Generic[T]):
    """
    Зависимые запросы к БД по значению поля: если у параметра нет значения или там
    массив (справочник), считаем выбор не сделанным — зависимые данные не подставляем.
    См. services.Changers.param_choice.is_scalar_choice.
    """

    @abstractmethod
    def changeData(self, data: T) -> T:
        """изменяет данные"""
        pass