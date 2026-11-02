from abc import ABC, abstractmethod


class Calculable(ABC):
    """Interfaz: el objeto sabe actualizar su propio total."""

    @abstractmethod
    def calcular_total(self) -> None:
        ...