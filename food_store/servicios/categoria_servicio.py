from typing import TYPE_CHECKING

from entidades import Categoria
from excepciones import (
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)

if TYPE_CHECKING:
    from servicios.producto_servicio import ProductoServicio


class CategoriaServicio:
    def __init__(self) -> None:
        self.__categorias: list[Categoria] = []

    def _existe_nombre(self, nombre: str, excluir_id: int | None = None) -> bool:
        """Compara sin distinguir mayúsculas, ignorando categorías eliminadas."""
        buscado = nombre.strip().casefold()
        return any(
            c.nombre.casefold() == buscado and not c.eliminado and c.id != excluir_id
            for c in self.__categorias
        )

    def crear(self, nombre: str, descripcion: str) -> Categoria:
        if self._existe_nombre(nombre):
            raise DuplicadoError(f"Ya existe una categoría llamada '{nombre.strip()}'")
        categoria = Categoria(nombre, descripcion)  # valida vacíos en los setters
        self.__categorias.append(categoria)
        return categoria

    def listar(self) -> list[Categoria]:
        return [c for c in self.__categorias if not c.eliminado]

    def obtener(self, id_categoria: int) -> Categoria:
        for c in self.__categorias:
            if c.id == id_categoria and not c.eliminado:
                return c
        raise EntidadNoEncontradaError(f"No existe la categoría con id {id_categoria}")

    def editar(
        self,
        id_categoria: int,
        nombre: str | None = None,
        descripcion: str | None = None,
    ) -> Categoria:
        """Los parámetros en None conservan el valor anterior."""
        categoria = self.obtener(id_categoria)
        if nombre is not None and self._existe_nombre(nombre, categoria.id):
            raise DuplicadoError(f"Ya existe una categoría llamada '{nombre.strip()}'")

        original = (categoria.nombre, categoria.descripcion)
        try:
            if nombre is not None:
                categoria.nombre = nombre
            if descripcion is not None:
                categoria.descripcion = descripcion
        except Exception:
            categoria.nombre, categoria.descripcion = original  # no queda a medias
            raise
        return categoria

    def eliminar(self, id_categoria: int, productos: "ProductoServicio") -> None:
        categoria = self.obtener(id_categoria)
        activos = productos.contar_activos_por_categoria(categoria)
        if activos > 0:
            raise OperacionNoPermitidaError(
                f"No se puede eliminar: la categoría tiene {activos} producto(s) activo(s)"
            )
        categoria.eliminado = True