from entidades import Usuario
from enums import Rol
from excepciones import (
    CredencialesInvalidasError,
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)


class UsuarioServicio:
    def __init__(self) -> None:
        self.__usuarios: list[Usuario] = []

    def _mail_en_uso(self, mail: str, excluir_id: int | None = None) -> bool:
        """Recorre toda la colección (incluye eliminados, porque siguen en ella)."""
        buscado = mail.strip().lower()
        return any(u.mail == buscado and u.id != excluir_id for u in self.__usuarios)

    def crear(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> Usuario:
        if self._mail_en_uso(mail):
            raise DuplicadoError(f"El mail '{mail.strip()}' ya está registrado")
        usuario = Usuario(nombre, apellido, mail, celular, contrasenia, rol)
        self.__usuarios.append(usuario)
        return usuario

    def listar(self) -> list[Usuario]:
        return [u for u in self.__usuarios if not u.eliminado]

    def obtener(self, id_usuario: int) -> Usuario:
        for u in self.__usuarios:
            if u.id == id_usuario and not u.eliminado:
                return u
        raise EntidadNoEncontradaError(f"No existe el usuario con id {id_usuario}")

    def editar(
        self,
        id_usuario: int,
        nombre: str | None = None,
        apellido: str | None = None,
        mail: str | None = None,
        celular: str | None = None,
        contrasenia: str | None = None,
        rol: Rol | None = None,
    ) -> Usuario:
        """Los parámetros en None conservan el valor anterior."""
        usuario = self.obtener(id_usuario)
        if mail is not None and self._mail_en_uso(mail, usuario.id):
            raise DuplicadoError(f"El mail '{mail.strip()}' ya está registrado")

        original = (
            usuario.nombre, usuario.apellido, usuario.mail, usuario.celular, usuario.rol
        )
        try:
            if nombre is not None:
                usuario.nombre = nombre
            if apellido is not None:
                usuario.apellido = apellido
            if mail is not None:
                usuario.mail = mail
            if celular is not None:
                usuario.celular = celular
            if rol is not None:
                usuario.rol = rol
            # La contraseña no se puede leer para respaldarla, por eso va última:
            # si falla, su setter valida antes de asignar y el resto se restaura.
            if contrasenia is not None:
                usuario.contrasenia = contrasenia
        except Exception:
            (usuario.nombre, usuario.apellido, usuario.mail,
             usuario.celular, usuario.rol) = original
            raise
        return usuario

    def eliminar(self, id_usuario: int, usuario_sesion: Usuario) -> None:
        usuario = self.obtener(id_usuario)
        if usuario == usuario_sesion:
            raise OperacionNoPermitidaError(
                "Un administrador no puede eliminarse a sí mismo mientras tiene la sesión iniciada"
            )
        usuario.eliminado = True

    def autenticar(self, mail: str, contrasenia: str) -> Usuario:
        mensaje = "Mail o contraseña incorrectos"  # mismo mensaje en los tres casos
        buscado = mail.strip().lower()
        for u in self.__usuarios:
            if u.mail == buscado:
                if u.eliminado or not u.verificar_contrasenia(contrasenia):
                    raise CredencialesInvalidasError(mensaje)
                return u
        raise CredencialesInvalidasError(mensaje)