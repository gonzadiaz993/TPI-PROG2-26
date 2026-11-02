from enum import Enum


class Estado(Enum):
    PENDIENTE = 1
    CONFIRMADO = 2
    TERMINADO = 3
    CANCELADO = 4