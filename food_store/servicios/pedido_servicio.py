from entidades import Pedido, Usuario
from enums import Estado, FormaPago
from excepciones import EntidadNoEncontradaError, OperacionNoPermitidaError
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio

TRANSICIONES: dict[Estado, frozenset[Estado]] = {
    Estado.PENDIENTE: frozenset({Estado.CONFIRMADO, Estado.CANCELADO}),
    Estado.CONFIRMADO: frozenset({Estado.TERMINADO, Estado.CANCELADO}),
    Estado.TERMINADO: frozenset(),
    Estado.CANCELADO: frozenset(),
}


class PedidoServicio:
    def __init__(self, usuarios: UsuarioServicio, productos: ProductoServicio) -> None:
        self.__usuarios: UsuarioServicio = usuarios
        self.__productos: ProductoServicio = productos
        self.__pedidos: list[Pedido] = []

    # ---------- Creación (en 3 pasos, para que la consola pueda ir validando) ----------

    def iniciar_pedido(self, id_usuario: int, forma_pago: FormaPago) -> Pedido:
        """Crea un pedido borrador: todavía NO está en la colección ni toca el stock."""
        usuario = self.__usuarios.obtener(id_usuario)  # existente y no eliminado
        return Pedido(usuario, forma_pago)

    def agregar_detalle(self, pedido: Pedido, id_producto: int, cantidad: int) -> None:
        producto = self.__productos.obtener(id_producto)  # existente y no eliminado
        if not producto.disponible:
            raise OperacionNoPermitidaError(f"El producto '{producto.nombre}' no está disponible")
        pedido.agregar_detalle(cantidad, producto)  # valida cantidad y stock, recalcula total

    def registrar(self, pedido: Pedido) -> Pedido:
        """Confirma la creación: guarda el pedido y descuenta el stock."""
        if pedido in self.__pedidos:
            raise OperacionNoPermitidaError("El pedido ya fue registrado")
        if not pedido.detalles:
            raise OperacionNoPermitidaError("El pedido debe tener al menos un detalle")

        # Primero se valida todo; recién después se descuenta (nada queda a medias)
        for d in pedido.detalles:
            if d.cantidad > d.producto.stock:
                self.__productos.descontar_stock(d.producto, d.cantidad)  # lanza el error
        for d in pedido.detalles:
            self.__productos.descontar_stock(d.producto, d.cantidad)

        pedido.calcular_total()
        self.__pedidos.append(pedido)
        return pedido

    def crear_pedido(
        self, id_usuario: int, forma_pago: FormaPago, items: list[tuple[int, int]]
    ) -> Pedido:
        """Atajo para pruebas: items = [(id_producto, cantidad), ...]."""
        pedido = self.iniciar_pedido(id_usuario, forma_pago)
        for id_producto, cantidad in items:
            self.agregar_detalle(pedido, id_producto, cantidad)
        return self.registrar(pedido)

    # ---------- Consultas ----------

    def listar(self) -> list[Pedido]:
        return [p for p in self.__pedidos if not p.eliminado]

    def listar_por_usuario(self, usuario: Usuario) -> list[Pedido]:
        """Funciona también con usuarios eliminados (sus pedidos se siguen consultando)."""
        return [p for p in self.listar() if p.usuario == usuario]

    def obtener(self, id_pedido: int) -> Pedido:
        for p in self.__pedidos:
            if p.id == id_pedido and not p.eliminado:
                return p
        raise EntidadNoEncontradaError(f"No existe el pedido con id {id_pedido}")

    def obtener_de_usuario(self, id_pedido: int, usuario: Usuario) -> Pedido:
        """Para el cliente: un pedido ajeno se informa como inexistente."""
        pedido = self.obtener(id_pedido)
        if pedido.usuario != usuario:
            raise EntidadNoEncontradaError(f"No existe el pedido con id {id_pedido}")
        return pedido

    # ---------- Modificaciones ----------

    def actualizar(
        self,
        id_pedido: int,
        estado: Estado | None = None,
        forma_pago: FormaPago | None = None,
    ) -> Pedido:
        pedido = self.obtener(id_pedido)

        if estado is not None and estado not in TRANSICIONES[pedido.estado]:
            raise OperacionNoPermitidaError(
                f"Transición inválida: {pedido.estado.name} → {estado.name}"
            )

        # Si llegó hasta acá, ya está todo validado
        if forma_pago is not None:
            pedido.forma_pago = forma_pago
        if estado is not None:
            pedido.estado = estado
            if estado == Estado.CANCELADO:
                self._devolver_stock(pedido)
        return pedido

    def eliminar(self, id_pedido: int) -> None:
        pedido = self.obtener(id_pedido)
        if pedido.estado not in (Estado.TERMINADO, Estado.CANCELADO):
            self._devolver_stock(pedido)
        for detalle in pedido.detalles:
            detalle.eliminado = True
        pedido.eliminado = True

    def _devolver_stock(self, pedido: Pedido) -> None:
        for d in pedido.detalles:
            self.__productos.devolver_stock(d.producto, d.cantidad)