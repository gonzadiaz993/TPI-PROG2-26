from datetime import date

from entidades.base import Base
from entidades.calculable import Calculable
from entidades.detalle_pedido import DetallePedido
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums import Estado, FormaPago
from excepciones import (
    DatoInvalidoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    StockInsuficienteError,
)


class Pedido(Base, Calculable):
    def __init__(self, usuario: Usuario, forma_pago: FormaPago) -> None:
        super().__init__()
        if not isinstance(usuario, Usuario):
            raise DatoInvalidoError("El pedido requiere un usuario")
        if usuario.eliminado:
            raise OperacionNoPermitidaError("No se puede crear un pedido con un usuario eliminado")
        self.__usuario: Usuario = usuario
        self.__fecha: date = date.today()
        self.__estado: Estado = Estado.PENDIENTE
        self.__total: float = 0.0
        self.__detalles: list[DetallePedido] = []
        self.forma_pago = forma_pago

    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def fecha(self) -> date:
        return self.__fecha

    @property
    def estado(self) -> Estado:
        return self.__estado

    @estado.setter
    def estado(self, valor: Estado) -> None:
        # Las transiciones válidas se controlan en PedidoServicio
        if not isinstance(valor, Estado):
            raise DatoInvalidoError("Estado inválido")
        self.__estado = valor

    @property
    def total(self) -> float:
        return self.__total

    @property
    def forma_pago(self) -> FormaPago:
        return self.__forma_pago

    @forma_pago.setter
    def forma_pago(self, valor: FormaPago) -> None:
        if not isinstance(valor, FormaPago):
            raise DatoInvalidoError("Forma de pago inválida")
        self.__forma_pago: FormaPago = valor

    @property
    def detalles(self) -> tuple[DetallePedido, ...]:
        return tuple(self.__detalles)

    def agregar_detalle(self, cantidad: int, producto: Producto) -> None:
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("Producto inválido")
        if producto.eliminado:
            raise OperacionNoPermitidaError("El producto está eliminado")
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser un entero mayor a 0")

        existente = self.buscar_detalle_por_producto(producto)
        cantidad_total = cantidad + (existente.cantidad if existente else 0)
        if cantidad_total > producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de '{producto.nombre}': "
                f"pedido {cantidad_total}, disponible {producto.stock}"
            )

        if existente:
            existente.cantidad = cantidad_total
        else:
            self.__detalles.append(DetallePedido(cantidad, producto))
        self.calcular_total()

    def buscar_detalle_por_producto(self, producto: Producto) -> DetallePedido | None:
        for detalle in self.__detalles:
            if detalle.producto == producto and not detalle.eliminado:
                return detalle
        return None

    def eliminar_detalle_por_producto(self, producto: Producto) -> None:
        detalle = self.buscar_detalle_por_producto(producto)
        if detalle is None:
            raise EntidadNoEncontradaError("El pedido no tiene ese producto")
        self.__detalles.remove(detalle)
        self.calcular_total()

    def calcular_total(self) -> None:
        self.__total = sum(d.subtotal for d in self.__detalles if not d.eliminado)

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.usuario.nombre} {self.usuario.apellido} | "
            f"{self.estado.name} | {self.forma_pago.name} | "
            f"${self.total:.2f} | {self.fecha}"
        )