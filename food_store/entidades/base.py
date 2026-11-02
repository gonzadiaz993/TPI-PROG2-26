from abc import ABC, abstractmethod
from datetime import datetime


class Base(ABC):
    """Superclase abstracta de todas las entidades.

    Usa un contador de clase compartido por todas las entidades,
    por lo que cada id es único en todo el sistema.
    Es abstracta porque obliga a las subclases a definir __str__.
    """

    __contador: int = 0

    def __init__(self) -> None:
        Base.__contador += 1
        self.__id: int = Base.__contador
        self.__eliminado: bool = False
        self.__creado_en: datetime = datetime.now()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def eliminado(self) -> bool:
        return self.__eliminado

    @eliminado.setter
    def eliminado(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise TypeError("'eliminado' debe ser booleano")
        self.__eliminado = valor

    @property
    def creado_en(self) -> datetime:
        return self.__creado_en

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Base):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self) -> int:
        return hash(self.id)

    @abstractmethod
    def __str__(self) -> str:
        ...