from entidades.base import Base
from entidades.categoria import Categoria
from excepciones import DatoInvalidoError, PrecioInvalidoError


class Producto(Base):
    def __init__(
        self,
        nombre: str,
        precio: float,
        stock: int,
        categoria: Categoria,
        descripcion: str = "",
        imagen: str = "",
        disponible: bool = True,
    ) -> None:
        super().__init__()
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
        self.descripcion = descripcion
        self.imagen = imagen
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El nombre del producto no puede estar vacío")
        self.__nombre: str = valor.strip()

    @property
    def precio(self) -> float:
        return self.__precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if valor < 0:
            raise PrecioInvalidoError("El precio no puede ser negativo")
        self.__precio: float = float(valor)

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("La descripción debe ser texto")
        self.__descripcion: str = valor.strip()

    @property
    def stock(self) -> int:
        return self.__stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise DatoInvalidoError("El stock debe ser un entero mayor o igual a 0")
        self.__stock: int = valor

    @property
    def imagen(self) -> str:
        return self.__imagen

    @imagen.setter
    def imagen(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("La imagen debe ser texto")
        self.__imagen: str = valor.strip()

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise DatoInvalidoError("La disponibilidad debe ser booleana")
        self.__disponible: bool = valor

    @property
    def categoria(self) -> Categoria:
        return self.__categoria

    @categoria.setter
    def categoria(self, valor: Categoria) -> None:
        if not isinstance(valor, Categoria):
            raise DatoInvalidoError("La categoría del producto es inválida")
        if valor.eliminado:
            raise DatoInvalidoError("La categoría está eliminada")
        self.__categoria: Categoria = valor

    def __str__(self) -> str:
        disp = "Sí" if self.disponible else "No"
        return (
            f"[{self.id}] {self.nombre} | ${self.precio:.2f} | "
            f"stock: {self.stock} | disp: {disp} | cat: {self.categoria.nombre}"
        )