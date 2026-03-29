from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from services.tech_card import TechCardData
T = TypeVar('T')

class IServise(ABC):
    @abstractmethod
    def get_template()->TechCardData:
        pass
    
    @abstractmethod
    def updateTechCard(data: T)->None:
        pass

