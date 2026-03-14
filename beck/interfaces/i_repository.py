from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        pass

    @abstractmethod
    def get_params_for_type(self, type_id):#получение параметров всех типов контролирующего элемента
        pass

    @abstractmethod
    def get_all_controlled_element_types(self)->T:#получение всех типов контролируемых эементов
        pass
    
    @abstractmethod
    def get_all_objects_by_type_id(self, type_id)->T:#получние все контролируемых элементов по id типа
        pass

    @abstractmethod
    def get_all_possible_values_by_param_and_element(self, element_type_id,param_id)->T:
        pass

    @abstractmethod
    def get_params_for_element(self, element_id: int) -> T:
        """Получить все параметры и их значения для конкретного элемента (objectControl) по его id."""
        pass

