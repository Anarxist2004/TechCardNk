from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from services.Interfaces.i_servise import IServise
from services.tech_card import TechCardData
T = TypeVar('T')

class IControllers(ABC, Generic[T]):

    @abstractmethod
    def get_template()->TechCardData:
        pass
    
    @abstractmethod
    def updateTechCard()->TechCardData:
        pass
