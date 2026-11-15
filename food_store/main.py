from consola import crear_menu, iniciar_sesion
from enums import Rol
from excepciones import FoodStoreError
from servicios import CategoriaServicio, PedidoServicio, ProductoServicio, UsuarioServicio


def cargar_datos_iniciales(
    usuarios: UsuarioServicio,
    categorias: CategoriaServicio,
    productos: ProductoServicio,
) -> None:
    """Administrador inicial y datos de ejemplo (solo si el sistema está vacío)."""
    try:
        if not usuarios.listar():
            usuarios.crear("Ana", "Pérez", "admin@foodstore.com", "2615550000", "admin123", Rol.ADMIN)
            usuarios.crear("Juan", "Gómez", "juan@foodstore.com", "2615551111", "juan123", Rol.USUARIO)
            print(">>> Usuarios iniciales creados: admin@foodstore.com / admin123 y juan@foodstore.com / juan123")

        if not categorias.listar():
            pizzas = categorias.crear("Pizzas", "Pizzas artesanales al horno de piedra")
            bebidas = categorias.crear("Bebidas", "Bebidas frías y refrescantes")
            productos.crear("Muzzarella", "Salsa de tomate, muzzarella y orégano",
                            6500.0, 15, "muzzarella.jpg", True, pizzas.id)
            productos.crear("Coca-Cola 1.5L", "Gaseosa sabor original",
                            2500.0, 20, "coca15.jpg", True, bebidas.id)
    except FoodStoreError as e:
        print(f"Aviso durante la inicialización: {e}")


def main() -> None:
    # Los servicios y la sesión se crean acá y se pasan a los menús (sin variables globales)
    categorias = CategoriaServicio()
    productos = ProductoServicio(categorias)
    usuarios = UsuarioServicio()
    pedidos = PedidoServicio(usuarios, productos)
    cargar_datos_iniciales(usuarios, categorias, productos)

    print("========================================")
    print("      BIENVENIDO/A A FOOD STORE")
    print("========================================")

    while True:
        usuario_sesion = iniciar_sesion(usuarios)
        if usuario_sesion is None:
            break
        menu = crear_menu(usuario_sesion, categorias, productos, usuarios, pedidos)
        if not menu.mostrar():  # False = salir del programa
            break

    print("\nGracias por utilizar Food Store. ¡Hasta luego!")


if __name__ == "__main__":
    main()
