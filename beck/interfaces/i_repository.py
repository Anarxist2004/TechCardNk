from abc import ABC, abstractmethod
from typing import Generic, TypeVar

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
    def get_params_for_type(self, type_id):
        pass

    @abstractmethod
    def get_all_controlled_element_types(self) -> T:
        pass

    @abstractmethod
    def get_all_objects_by_type_id(self, type_id) -> T:
        pass

    @abstractmethod
    def get_all_possible_values_by_param_and_element(self, element_type_id, param_id) -> T:
        pass

    @abstractmethod
    def get_params_for_element(self, element_id: int) -> T:
        pass

    @abstractmethod
    def create_param_option(self, payload: dict) -> dict:
        pass

    def sync_tech_card(self, tech_card: T) -> T:
        return tech_card
