from entidades import Categoria, Producto
from excepciones import EntidadNoEncontradaError, StockInsuficienteError
from servicios.categoria_servicio import CategoriaServicio


class ProductoServicio:
    def __init__(self, categorias: CategoriaServicio) -> None:
        self.__categorias: CategoriaServicio = categorias
        self.__productos: list[Producto] = []

    def crear(
        self,
        nombre: str,
        descripcion: str,
        precio: float,
        stock: int,
        imagen: str,
        disponible: bool,
        id_categoria: int,
    ) -> Producto:
        categoria = self.__categorias.obtener(id_categoria)  # existente y no eliminada
        producto = Producto(
            nombre, precio, stock, categoria,
            descripcion=descripcion, imagen=imagen, disponible=disponible,
        )
        self.__productos.append(producto)
        return producto

    def listar(self, id_categoria: int | None = None) -> list[Producto]:
        """Todos los no eliminados (vista del administrador). Filtro opcional por categoría."""
        resultado = [p for p in self.__productos if not p.eliminado]
        if id_categoria is not None:
            resultado = [p for p in resultado if p.categoria.id == id_categoria]
        return resultado

    def listar_disponibles(self, id_categoria: int | None = None) -> list[Producto]:
        """Vista del cliente: no eliminados, disponibles y con stock > 0."""
        return [p for p in self.listar(id_categoria) if p.disponible and p.stock > 0]

    def obtener(self, id_producto: int) -> Producto:
        for p in self.__productos:
            if p.id == id_producto and not p.eliminado:
                return p
        raise EntidadNoEncontradaError(f"No existe el producto con id {id_producto}")

    def editar(
        self,
        id_producto: int,
        nombre: str | None = None,
        descripcion: str | None = None,
        precio: float | None = None,
        stock: int | None = None,
        imagen: str | None = None,
        disponible: bool | None = None,
        id_categoria: int | None = None,
    ) -> Producto:
        """Los parámetros en None conservan el valor anterior."""
        producto = self.obtener(id_producto)
        categoria_nueva = (
            self.__categorias.obtener(id_categoria) if id_categoria is not None else None
        )

        original = (
            producto.nombre, producto.descripcion, producto.precio, producto.stock,
            producto.imagen, producto.disponible, producto.categoria,
        )
        try:
            if nombre is not None:
                producto.nombre = nombre
            if descripcion is not None:
                producto.descripcion = descripcion
            if precio is not None:
                producto.precio = precio
            if stock is not None:
                producto.stock = stock
            if imagen is not None:
                producto.imagen = imagen
            if disponible is not None:
                producto.disponible = disponible
            if categoria_nueva is not None:
                producto.categoria = categoria_nueva
        except Exception:
            (producto.nombre, producto.descripcion, producto.precio, producto.stock,
             producto.imagen, producto.disponible, producto.categoria) = original
            raise
        return producto

    def eliminar(self, id_producto: int) -> None:
        self.obtener(id_producto).eliminado = True

    def contar_activos_por_categoria(self, categoria: Categoria) -> int:
        return sum(
            1 for p in self.__productos
            if not p.eliminado and p.categoria == categoria
        )

    def descontar_stock(self, producto: Producto, cantidad: int) -> None:
        if cantidad > producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de '{producto.nombre}': "
                f"pedido {cantidad}, disponible {producto.stock}"
            )
        producto.stock -= cantidad

    def devolver_stock(self, producto: Producto, cantidad: int) -> None:
        producto.stock += cantidad