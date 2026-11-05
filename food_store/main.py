from enums import Rol, FormaPago
from excepciones import FoodStoreError, CredencialesInvalidasError
from servicios import CategoriaServicio, ProductoServicio, UsuarioServicio, PedidoServicio


def inicializar_sistema_base(
    usuarios: UsuarioServicio,
    categorias: CategoriaServicio,
    productos: ProductoServicio
) -> None:
    """
    Verifica si existen usuarios cargados (desde el CSV). 
    Si está completamente vacío (primer inicio), crea el administrador por defecto.
    """
    try:
        # Si no hay usuarios en memoria (el CSV no existía o estaba vacío), creamos el admin inicial
        if not usuarios.listar():
            usuarios.crear(
                nombre="Ana",
                apellido="Pérez",
                mail="admin@foodstore.com",
                celular="2615550000",
                contrasenia="admin123",
                rol=Rol.ADMIN
            )
            print(">>> Se ha creado el usuario Administrador por defecto (admin@foodstore.com / admin123).")

        # Las categorías y productos de prueba pueden mantenerse o gestionarse también,
        # pero dejamos una carga básica si no hay categorías creadas
        if not categorias.listar():
            cat_pizzas = categorias.crear("Pizzas", "Pizzas artesanales al horno de piedra")
            cat_bebidas = categorias.crear("Bebidas", "Bebidas frías y refrescantes")

            productos.crear(
                nombre="Muzzarella",
                descripcion="Salsa de tomate, mozzarella y orégano",
                precio=6500.0,
                stock=15,
                imagen="muzzarella.jpg",
                disponible=True,
                id_categoria=cat_pizzas.id
            )
            productos.crear(
                nombre="Coca-Cola 1.5L",
                descripcion="Gaseosa sabor original",
                precio=2500.0,
                stock=20,
                imagen="coca15.jpg",
                disponible=True,
                id_categoria=cat_bebidas.id
            )
    except FoodStoreError as e:
        print(f"Aviso durante la inicialización: {e}")


def mostrar_menu_administrador(usuario_actual, categorias, productos, usuarios, pedidos) -> bool:
    while True:
        print(f"\n=== FOOD STORE ADMINISTRADOR ({usuario_actual.nombre} {usuario_actual.apellido}) ===")
        print("1. Gestionar Categorías")
        print("2. Gestionar Productos")
        print("3. Ver Usuarios Registrados")
        print("4. Gestionar Pedidos")
        print("5. Registrar nuevo usuar io")
        print("9. Cerrar sesión")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n--- CATEGORÍAS ---")
            print("1. Listar | 2. Crear | 0. Volver")
            sub = input("Opción: ").strip()
            if sub == "1":
                cats = categorias.listar()
                if not cats:
                    print("No hay categorías cargadas.")
                for c in cats:
                    print(c)
            elif sub == "2":
                try:
                    nombre = input("Nombre: ")
                    desc = input("Descripción: ")
                    nueva = categorias.crear(nombre, desc)
                    print(f"¡Categoría creada con éxito! ID: {nueva.id}")
                except FoodStoreError as e:
                    print(f"Error de negocio: {e}")
        elif opcion == "2":
            print("\n--- PRODUCTOS ---")
            print("1. Listar | 2. Crear | 0. Volver")
            sub = input("Opción: ").strip()
            if sub == "1":
                prods = productos.listar()
                if not prods:
                    print("No hay productos cargados.")
                for p in prods:
                    print(p)
            elif sub == "2":
                try:
                    nombre = input("Nombre: ")
                    desc = input("Descripción: ")
                    precio = float(input("Precio: "))
                    stock = int(input("Stock: "))
                    imagen = input("Imagen (opcional): ")
                    disp_str = input("¿Disponible? (s/n): ").strip().lower()
                    disponible = disp_str == 's'
                    
                    print("\nCategorías disponibles:")
                    for c in categorias.listar():
                        print(f"ID {c.id}: {c.nombre}")
                    id_cat = int(input("ID de Categoría: "))
                    
                    p_nuevo = productos.crear(nombre, desc, precio, stock, imagen, disponible, id_cat)
                    print(f"¡Producto creado con éxito! ID: {p_nuevo.id}")
                except (ValueError, FoodStoreError) as e:
                    print(f"Error al crear producto: {e}")
        elif opcion == "3":
            print("\n--- USUARIOS REGISTRADOS (DESDE CSV) ---")
            for u in usuarios.listar():
                print(u)
        elif opcion == "4":
            print("\n--- PEDIDOS ---")
            print("1. Listar | 0. Volver")
            sub = input("Opción: ").strip()
            if sub == "1":
                peds = pedidos.listar()
                if not peds:
                    print("No hay pedidos registrados.")
                for p in peds:
                    print(p)
        elif opcion == "5":
            print("\n--- REGISTRAR NUEVO USUARIO ---")
            try:
                nombre = input("Nombre: ").strip()
                apellido = input("Apellido: ").strip()
                mail = input("Mail: ").strip()
                celular = input("Celular: ").strip()
                contrasenia = input("Contraseña: ").strip()
                
                print("\nSeleccione el rol:")
                print("1. Administrador")
                print("2. Usuario / Cliente")
                op_rol = input("Opción (1/2): ").strip()
                
                rol = Rol.ADMIN if op_rol == "1" else Rol.USUARIO
                
                nuevo_usuario = usuarios.crear(nombre, apellido, mail, celular, contrasenia, rol)
                print(f"¡Usuario registrado con éxito! ID: {nuevo_usuario.id} | {nuevo_usuario.mail} [{nuevo_usuario.rol.name}]")
            except FoodStoreError as e:
                print(f"Error de validación: {e}")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")
        elif opcion == "9":
            print("Cerrando sesión...")
            return True
        elif opcion == "0":
            print("Saliendo del sistema...")
            return False
        else:
            print("Opción inválida.")


def mostrar_menu_cliente(usuario_actual, categorias, productos, pedidos) -> bool:
    while True:
        print(f"\n=== FOOD STORE CLIENTE ({usuario_actual.nombre} {usuario_actual.apellido}) ===")
        print("1. Ver categorías")
        print("2. Ver productos disponibles")
        print("3. Mis pedidos")
        print("4. Mis datos")
        print("9. Cerrar sesión")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            for c in categorias.listar():
                print(c)
        elif opcion == "2":
            for p in productos.listar_disponibles():
                print(p)
        elif opcion == "3":
            mis_peds = pedidos.listar_por_usuario(usuario_actual)
            if not mis_peds:
                print("No tenés pedidos registrados.")
            for p in mis_peds:
                print(p)
        elif opcion == "4":
            print(f"Datos de tu cuenta: {usuario_actual}")
        elif opcion == "9":
            print("Cerrando sesión...")
            return True
        elif opcion == "0":
            print("Saliendo del sistema...")
            return False
        else:
            print("Opción inválida.")


def main() -> None:
    # 1. Inicialización de servicios (UsuarioServicio lee automáticamente el CSV)
    categorias_serv = CategoriaServicio()
    productos_serv = ProductoServicio(categorias_serv)
    usuarios_serv = UsuarioServicio()
    pedidos_serv = PedidoServicio(usuarios_serv, productos_serv)

    # 2. Inicializar sistema base (crea el admin en el CSV solo si no existe ninguno)
    inicializar_sistema_base(usuarios_serv, categorias_serv, productos_serv)

    print("========================================")
    print("   BIENVENIDO/A A FOOD STORE (SISTEMA)  ")
    print("========================================")

    # 3. Bucle principal de ejecución del programa
    app_corriendo = True
    while app_corriendo:
        intentos = 3
        usuario_sesion = None

        while intentos > 0 and usuario_sesion is None:
            print(f"\n--- INICIO DE SESIÓN (Intentos restantes: {intentos}) ---")
            mail = input("Mail: ").strip()
            contrasenia = input("Contraseña: ").strip()

            try:
                usuario_sesion = usuarios_serv.autenticar(mail, contrasenia)
            except CredencialesInvalidasError:
                intentos -= 1
                print("Mail o contraseña incorrectos.")
            except FoodStoreError as e:
                intentos -= 1
                print(f"Error: {e}")

        if usuario_sesion is None:
            print("\nSe han agotado los intentos permitidos. El programa ha finalizado.")
            break

        print(f"\n¡Bienvenido/a, {usuario_sesion.nombre} {usuario_sesion.apellido} [{usuario_sesion.rol.name}]!")

        if usuario_sesion.rol == Rol.ADMIN:
            continuar_sesion = mostrar_menu_administrador(
                usuario_sesion, categorias_serv, productos_serv, usuarios_serv, pedidos_serv
            )
        else:
            continuar_sesion = mostrar_menu_cliente(
                usuario_sesion, categorias_serv, productos_serv, pedidos_serv
            )

        if not continuar_sesion:
            app_corriendo = False

    print("\nGracias por utilizar Food Store. ¡Hasta luego!")


if __name__ == "__main__":
    main()