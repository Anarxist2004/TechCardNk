from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from interfaces.i_servise import IServise
T = TypeVar('T')

class IControllers(ABC, Generic[T]):
    @abstractmethod
    def handle_request(self, data: T) -> T:
        """Обрабатывает входные данные и возвращает результат"""
        pass    

    @abstractmethod
    def setServise(self,sertv:IServise):
        pass

    @abstractmethod
    def getObjectControl(self)->T:
        pass

    @abstractmethod
    def getControlElements(self,id)->T:
        pass

    @abstractmethod
    def getControlElementParam(self,id)->T:
        pass

    @abstractmethod
    def getElementParamsValues(self,id)->T:
        pass

    @abstractmethod
    def getControlElementParamValue(self,idCntlEl,idParam)->T:
        pass

    @abstractmethod
    def updateTechCard(self,techCard)->T:
        pass
    
    # @abstractmethod
    # def selectionOfControlObject(self)->T:

    # def 
