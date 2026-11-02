from entidades.base import Base
from entidades.producto import Producto
from excepciones import DatoInvalidoError


class DetallePedido(Base):
    """Solo debe ser creado por Pedido (composición)."""

    def __init__(self, cantidad: int, producto: Producto) -> None:
        super().__init__()
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("El detalle requiere un producto válido")
        self.__producto: Producto = producto
        # Precio congelado al momento de agregar el detalle
        self.__precio_unitario: float = producto.precio
        self.__subtotal: float = 0.0
        self.cantidad = cantidad

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise DatoInvalidoError("La cantidad debe ser un entero mayor a 0")
        self.__cantidad: int = valor
        self.__subtotal = self.__cantidad * self.__precio_unitario

    @property
    def subtotal(self) -> float:
        return self.__subtotal

    @property
    def producto(self) -> Producto:
        return self.__producto

    @property
    def precio_unitario(self) -> float:
        return self.__precio_unitario

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.producto.nombre} x{self.cantidad} "
            f"@ ${self.precio_unitario:.2f} = ${self.subtotal:.2f}"
        )