from entidades import Usuario
from excepciones import FoodStoreError
from servicios import UsuarioServicio
from consola.lectura import OperacionCanceladaError, pedir_contrasenia, pedir_texto


def iniciar_sesion(usuarios: UsuarioServicio, intentos: int = 3) -> Usuario | None:
    """Pide mail y contraseña (hasta 3 intentos). Devuelve None si no se pudo ingresar."""
    print("\n=== FOOD STORE – INICIO DE SESIÓN ===")
    for restantes in range(intentos, 0, -1):
        try:
            mail = pedir_texto("Mail")
            contrasenia = pedir_contrasenia("Contraseña", obligatoria=False)
        except OperacionCanceladaError:
            return None
        try:
            usuario = usuarios.autenticar(mail, contrasenia)
        except FoodStoreError as e:
            print(f"✗ {e}. Intentos restantes: {restantes - 1}")
            continue
        print(f"\nBienvenido/a, {usuario.nombre} {usuario.apellido} [{usuario.rol.name}]")
        return usuario
    print("\nSe agotaron los intentos permitidos. El programa finaliza.")
    return None
