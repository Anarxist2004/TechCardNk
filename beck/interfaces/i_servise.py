from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from services.tech_card import TechCardData
T = TypeVar('T')

class IServise(ABC):
    @abstractmethod
    def findNewParamsByTechCard(data: T)->None:
        pass
    
    @abstractmethod
    def setData(data: T)->None:
        pass

    @abstractmethod
    def getObjectControl(self, methodology=0)->T:
        pass

    @abstractmethod
    def getControlElements(self,id, methodology=0)->T:
        pass

    @abstractmethod
    def getControlElementParam(self,id, methodology=0)->T:
        pass

    @abstractmethod
    def geElementParamsValue(self,id, methodology=0)->T:
        pass

    @abstractmethod
    def getControlElementParamValue(self,idCntlEl,idParam)->T:
        pass

    @abstractmethod
    def updateTechCard(self,techCard)->T:
        pass

    @abstractmethod
    def getMethodologies(self)->T:
        pass
