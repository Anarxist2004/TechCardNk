from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    def __init__(self):
        return