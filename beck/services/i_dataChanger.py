from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from interfaces.i_servise import IServise
T = TypeVar('T')

class IDataChanger(ABC, Generic[T]):

    @abstractmethod
    def changeData(self, data: T) -> T:
        """изменяет данные"""
        pass   