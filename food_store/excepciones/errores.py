class FoodStoreError(Exception):
    """Excepción base de todo el sistema."""


class EntidadNoEncontradaError(FoodStoreError):
    """Id inexistente o entidad eliminada."""


class DatoInvalidoError(FoodStoreError):
    """Texto vacío, formato incorrecto, valor fuera de rango."""


class PrecioInvalidoError(DatoInvalidoError):
    """Precio negativo o inválido."""


class StockInsuficienteError(FoodStoreError):
    """Cantidad pedida mayor al stock disponible."""


class DuplicadoError(FoodStoreError):
    """Mail o nombre de categoría repetido."""


class OperacionNoPermitidaError(FoodStoreError):
    """Transición inválida, categoría con productos activos, etc."""


class CredencialesInvalidasError(FoodStoreError):
    """Mail o contraseña incorrectos, o usuario eliminado."""