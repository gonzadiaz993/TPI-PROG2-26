from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any

from questionary import Style

from entidades import Pedido, Usuario
from enums import Estado, FormaPago, Rol
from excepciones import DatoInvalidoError, DuplicadoError, FoodStoreError
from servicios import CategoriaServicio, PedidoServicio, ProductoServicio, UsuarioServicio
from consola.lectura import (
    ESTILO_ADMIN,
    ESTILO_CLIENTE,
    OperacionCanceladaError,
    elegir,
    elegir_enum,
    elegir_enum_opcional,
    pedir_contrasenia,
    pedir_decimal,
    pedir_decimal_opcional,
    pedir_entero,
    pedir_entero_opcional,
    pedir_si_no,
    pedir_si_no_opcional,
    pedir_texto,
    pedir_texto_libre,
    pedir_texto_opcional,
)

Accion = Callable[[], None]
_VOLVER: object = object()
_CERRAR: object = object()
_SALIR: object = object()


class Menu(ABC):
    """Clase abstracta: cada rol define su propio menú (polimorfismo)."""

    _estilo: Style | None = None

    def __init__(self, usuario: Usuario) -> None:
        self._usuario: Usuario = usuario

    @abstractmethod
    def mostrar(self) -> bool:
        """True = cerrar sesión, False = salir del programa."""

    # ---------- Utilidades comunes ----------

    def _bucle_principal(self, titulo: str, opciones: list[tuple[str, Any]]) -> bool:
        entradas = [*opciones, ("9. Cerrar sesión", _CERRAR), ("0. Salir", _SALIR)]
        while True:
            try:
                accion = elegir(f"\n{titulo}", entradas, self._estilo)
            except OperacionCanceladaError:
                return False
            if accion is _CERRAR:
                print("Cerrando sesión...")
                return True
            if accion is _SALIR:
                print("Saliendo del sistema...")
                return False
            self._ejecutar(accion)

    def _submenu(self, titulo: str, opciones: list[tuple[str, Accion]]) -> None:
        entradas: list[tuple[str, Any]] = [*opciones, ("0. Volver", _VOLVER)]
        while True:
            try:
                accion = elegir(f"\n--- {titulo} ---", entradas, self._estilo)
            except OperacionCanceladaError:
                return
            if accion is _VOLVER:
                return
            self._ejecutar(accion)

    @staticmethod
    def _ejecutar(accion: Accion) -> None:
        """Ningún error cierra el programa: se informa y se vuelve al menú."""
        try:
            accion()
        except FoodStoreError as e:
            print(f"✗ Error: {e}")
        except ValueError as e:
            print(f"✗ Dato inválido: {e}")
        except OperacionCanceladaError:
            print("Operación cancelada.")

    @staticmethod
    def _imprimir_lista(items: Sequence[object], vacio: str) -> None:
        if not items:
            print(vacio)
            return
        for item in items:
            print(item)

    @staticmethod
    def _imprimir_pedido(pedido: Pedido) -> None:
        print(pedido)
        for detalle in pedido.detalles:
            print(f"    • {detalle}")
        print(f"    Total: ${pedido.total:.2f}")


class MenuAdministrador(Menu):
    _estilo = ESTILO_ADMIN

    def __init__(
        self,
        usuario: Usuario,
        categorias: CategoriaServicio,
        productos: ProductoServicio,
        usuarios: UsuarioServicio,
        pedidos: PedidoServicio,
    ) -> None:
        super().__init__(usuario)
        self._categorias: CategoriaServicio = categorias
        self._productos: ProductoServicio = productos
        self._usuarios: UsuarioServicio = usuarios
        self._pedidos: PedidoServicio = pedidos

    def mostrar(self) -> bool:
        titulo = f"=== FOOD STORE – ADMINISTRADOR ({self._usuario.nombre} {self._usuario.apellido}) ==="
        return self._bucle_principal(titulo, [
            ("1. Categorías", self._menu_categorias),
            ("2. Productos", self._menu_productos),
            ("3. Usuarios", self._menu_usuarios),
            ("4. Pedidos", self._menu_pedidos),
        ])

    # ================= CATEGORÍAS =================

    def _menu_categorias(self) -> None:
        self._submenu("CATEGORÍAS", [
            ("1. Listar", self._listar_categorias),
            ("2. Crear", self._crear_categoria),
            ("3. Editar", self._editar_categoria),
            ("4. Eliminar", self._eliminar_categoria),
        ])

    def _listar_categorias(self) -> None:
        self._imprimir_lista(self._categorias.listar(), "No hay categorías cargadas.")

    def _crear_categoria(self) -> None:
        nombre = pedir_texto("Nombre")
        descripcion = pedir_texto("Descripción")
        categoria = self._categorias.crear(nombre, descripcion)
        print(f"✓ Categoría creada. ID: {categoria.id}")

    def _editar_categoria(self) -> None:
        self._listar_categorias()
        categoria = self._categorias.obtener(pedir_entero("ID de la categoría"))
        nombre = pedir_texto_opcional("Nombre", categoria.nombre)
        descripcion = pedir_texto_opcional("Descripción", categoria.descripcion)
        self._categorias.editar(categoria.id, nombre, descripcion)
        print("✓ Categoría actualizada.")

    def _eliminar_categoria(self) -> None:
        self._listar_categorias()
        categoria = self._categorias.obtener(pedir_entero("ID de la categoría"))
        if not pedir_si_no(f"¿Eliminar la categoría '{categoria.nombre}'?"):
            print("Operación cancelada.")
            return
        self._categorias.eliminar(categoria.id, self._productos)
        print("✓ Categoría eliminada.")

    # ================= PRODUCTOS =================

    def _menu_productos(self) -> None:
        self._submenu("PRODUCTOS", [
            ("1. Listar", self._listar_productos),
            ("2. Listar por categoría", self._listar_productos_por_categoria),
            ("3. Crear", self._crear_producto),
            ("4. Editar", self._editar_producto),
            ("5. Eliminar", self._eliminar_producto),
        ])

    def _listar_productos(self) -> None:
        self._imprimir_lista(self._productos.listar(), "No hay productos cargados.")

    def _listar_productos_por_categoria(self) -> None:
        self._imprimir_lista(self._categorias.listar(), "No hay categorías cargadas.")
        id_categoria = pedir_entero("ID de la categoría")
        categoria = self._categorias.obtener(id_categoria)
        self._imprimir_lista(
            self._productos.listar(categoria.id), "No hay productos en esa categoría."
        )

    def _crear_producto(self) -> None:
        nombre = pedir_texto("Nombre")
        descripcion = pedir_texto("Descripción")
        precio = pedir_decimal("Precio")
        stock = pedir_entero("Stock")
        imagen = pedir_texto_libre("Imagen (opcional)")
        disponible = pedir_si_no("¿Disponible?")
        print("\nCategorías disponibles:")
        self._listar_categorias()
        id_categoria = pedir_entero("ID de la categoría")
        producto = self._productos.crear(
            nombre, descripcion, precio, stock, imagen, disponible, id_categoria
        )
        print(f"✓ Producto creado. ID: {producto.id}")

    def _editar_producto(self) -> None:
        self._listar_productos()
        producto = self._productos.obtener(pedir_entero("ID del producto"))
        nombre = pedir_texto_opcional("Nombre", producto.nombre)
        descripcion = pedir_texto_opcional("Descripción", producto.descripcion)
        precio = pedir_decimal_opcional("Precio", producto.precio)
        stock = pedir_entero_opcional("Stock", producto.stock)
        imagen = pedir_texto_opcional("Imagen", producto.imagen)
        disponible = pedir_si_no_opcional("¿Disponible?", producto.disponible)
        self._listar_categorias()
        id_categoria = pedir_entero_opcional("ID de categoría", producto.categoria.id)
        self._productos.editar(
            producto.id, nombre, descripcion, precio, stock, imagen, disponible, id_categoria
        )
        print("✓ Producto actualizado.")

    def _eliminar_producto(self) -> None:
        self._listar_productos()
        producto = self._productos.obtener(pedir_entero("ID del producto"))
        if not pedir_si_no(f"¿Eliminar el producto '{producto.nombre}'?"):
            print("Operación cancelada.")
            return
        self._productos.eliminar(producto.id)
        print("✓ Producto eliminado.")

    # ================= USUARIOS =================

    def _menu_usuarios(self) -> None:
        self._submenu("USUARIOS", [
            ("1. Listar", self._listar_usuarios),
            ("2. Crear", self._crear_usuario),
            ("3. Editar", self._editar_usuario),
            ("4. Eliminar", self._eliminar_usuario),
        ])

    def _listar_usuarios(self) -> None:
        self._imprimir_lista(self._usuarios.listar(), "No hay usuarios cargados.")

    def _crear_usuario(self) -> None:
        nombre = pedir_texto("Nombre")
        apellido = pedir_texto("Apellido")
        celular = pedir_texto("Celular")
        contrasenia = pedir_contrasenia()
        rol = elegir_enum("Rol", Rol, self._estilo)
        while True:  # si el mail es inválido o ya existe, se informa y se pide otro
            mail = pedir_texto("Mail")
            try:
                usuario = self._usuarios.crear(nombre, apellido, mail, celular, contrasenia, rol)
                break
            except (DuplicadoError, DatoInvalidoError) as e:
                print(f"✗ {e}. Ingresá otro mail.")
        print(f"✓ Usuario creado. ID: {usuario.id} | {usuario.mail} [{usuario.rol.name}]")

    def _editar_usuario(self) -> None:
        self._listar_usuarios()
        usuario = self._usuarios.obtener(pedir_entero("ID del usuario"))
        nombre = pedir_texto_opcional("Nombre", usuario.nombre)
        apellido = pedir_texto_opcional("Apellido", usuario.apellido)
        mail = pedir_texto_opcional("Mail", usuario.mail)
        celular = pedir_texto_opcional("Celular", usuario.celular)
        contrasenia = pedir_contrasenia("Nueva contraseña (Enter conserva)", obligatoria=False)
        rol = elegir_enum_opcional("Rol", Rol, usuario.rol, self._estilo)
        self._usuarios.editar(
            usuario.id, nombre, apellido, mail, celular, contrasenia or None, rol
        )
        print("✓ Usuario actualizado.")

    def _eliminar_usuario(self) -> None:
        self._listar_usuarios()
        usuario = self._usuarios.obtener(pedir_entero("ID del usuario"))
        if not pedir_si_no(f"¿Eliminar al usuario '{usuario.mail}'?"):
            print("Operación cancelada.")
            return
        self._usuarios.eliminar(usuario.id, self._usuario)
        print("✓ Usuario eliminado.")

    # ================= PEDIDOS =================

    def _menu_pedidos(self) -> None:
        self._submenu("PEDIDOS", [
            ("1. Listar", self._listar_pedidos),
            ("2. Listar por usuario", self._listar_pedidos_por_usuario),
            ("3. Ver detalle de un pedido", self._ver_detalle_pedido),
            ("4. Crear", self._crear_pedido),
            ("5. Cambiar estado / forma de pago", self._actualizar_pedido),
            ("6. Eliminar", self._eliminar_pedido),
        ])

    def _listar_pedidos(self) -> None:
        self._imprimir_lista(self._pedidos.listar(), "No hay pedidos registrados.")

    def _listar_pedidos_por_usuario(self) -> None:
        self._listar_usuarios()
        usuario = self._usuarios.obtener(pedir_entero("ID del usuario"))
        self._imprimir_lista(
            self._pedidos.listar_por_usuario(usuario), "Ese usuario no tiene pedidos."
        )

    def _ver_detalle_pedido(self) -> None:
        self._listar_pedidos()
        self._imprimir_pedido(self._pedidos.obtener(pedir_entero("ID del pedido")))

    def _crear_pedido(self) -> None:
        self._listar_usuarios()
        id_usuario = pedir_entero("ID del usuario")
        forma_pago = elegir_enum("Forma de pago", FormaPago, self._estilo)
        pedido = self._pedidos.iniciar_pedido(id_usuario, forma_pago)
        try:
            while True:
                self._imprimir_lista(
                    self._productos.listar_disponibles(), "No hay productos disponibles."
                )
                id_producto = pedir_entero("ID del producto")
                cantidad = pedir_entero("Cantidad")
                self._pedidos.agregar_detalle(pedido, id_producto, cantidad)
                print(f"✓ Agregado. Total parcial: ${pedido.total:.2f}")
                if not pedir_si_no("¿Agregar otro producto?"):
                    break
            self._pedidos.registrar(pedido)
        except FoodStoreError as e:
            print(f"✗ Error: {e}")
            print("Se cancela la creación del pedido: no se modificó ningún stock.")
            return
        print(f"✓ Pedido creado. ID: {pedido.id} | Total: ${pedido.total:.2f}")

    def _actualizar_pedido(self) -> None:
        self._listar_pedidos()
        pedido = self._pedidos.obtener(pedir_entero("ID del pedido"))
        estado = elegir_enum_opcional("Nuevo estado", Estado, pedido.estado, self._estilo)
        forma_pago = elegir_enum_opcional(
            "Nueva forma de pago", FormaPago, pedido.forma_pago, self._estilo
        )
        if estado is None and forma_pago is None:
            print("No se indicó ningún cambio.")
            return
        self._pedidos.actualizar(pedido.id, estado, forma_pago)
        print("✓ Pedido actualizado.")

    def _eliminar_pedido(self) -> None:
        self._listar_pedidos()
        pedido = self._pedidos.obtener(pedir_entero("ID del pedido"))
        if not pedir_si_no(f"¿Eliminar el pedido {pedido.id}?"):
            print("Operación cancelada.")
            return
        self._pedidos.eliminar(pedido.id)
        print("✓ Pedido eliminado.")


class MenuCliente(Menu):
    """Solo consulta: ninguna opción modifica datos."""

    _estilo = ESTILO_CLIENTE

    def __init__(
        self,
        usuario: Usuario,
        categorias: CategoriaServicio,
        productos: ProductoServicio,
        pedidos: PedidoServicio,
    ) -> None:
        super().__init__(usuario)
        self._categorias: CategoriaServicio = categorias
        self._productos: ProductoServicio = productos
        self._pedidos: PedidoServicio = pedidos

    def mostrar(self) -> bool:
        titulo = f"=== FOOD STORE – CLIENTE ({self._usuario.nombre} {self._usuario.apellido}) ==="
        return self._bucle_principal(titulo, [
            ("1. Ver categorías", self._ver_categorias),
            ("2. Ver productos disponibles", self._ver_productos),
            ("3. Mis pedidos", self._mis_pedidos),
            ("4. Mis datos", self._mis_datos),
        ])

    def _ver_categorias(self) -> None:
        self._imprimir_lista(self._categorias.listar(), "No hay categorías cargadas.")

    def _ver_productos(self) -> None:
        self._imprimir_lista(
            self._productos.listar_disponibles(), "No hay productos disponibles."
        )

    def _mis_pedidos(self) -> None:
        pedidos = self._pedidos.listar_por_usuario(self._usuario)
        self._imprimir_lista(pedidos, "No tenés pedidos registrados.")
        if not pedidos:
            return
        id_pedido = pedir_entero_opcional("ID del pedido para ver el detalle (Enter para volver)")
        if id_pedido is None:
            return
        # Un pedido de otro usuario se informa como inexistente
        self._imprimir_pedido(self._pedidos.obtener_de_usuario(id_pedido, self._usuario))

    def _mis_datos(self) -> None:
        u = self._usuario
        print(f"Nombre:   {u.nombre}")
        print(f"Apellido: {u.apellido}")
        print(f"Mail:     {u.mail}")
        print(f"Celular:  {u.celular}")
        print(f"Rol:      {u.rol.name}")


def crear_menu(
    usuario: Usuario,
    categorias: CategoriaServicio,
    productos: ProductoServicio,
    usuarios: UsuarioServicio,
    pedidos: PedidoServicio,
) -> Menu:
    """Único lugar del programa donde se decide el menú según el rol."""
    if usuario.rol == Rol.ADMIN:
        return MenuAdministrador(usuario, categorias, productos, usuarios, pedidos)
    return MenuCliente(usuario, categorias, productos, pedidos)
