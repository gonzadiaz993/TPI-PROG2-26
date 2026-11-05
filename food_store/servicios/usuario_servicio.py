import csv
import os
from entidades import Usuario
from enums import Rol
from excepciones import (
    CredencialesInvalidasError,
    DuplicadoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    DatoInvalidoError,
)

ARCHIVO_CSV = "usuarios.csv"


class UsuarioServicio:
    def __init__(self) -> None:
        self.__usuarios: list[Usuario] = []
        self._cargar_desde_csv()

    def _cargar_desde_csv(self) -> None:
        """Carga los usuarios desde el archivo CSV al iniciar el servicio."""
        if not os.path.exists(ARCHIVO_CSV):
            return
        
        try:
            with open(ARCHIVO_CSV, mode="r", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    # Evitamos duplicados si ya estuvieran en memoria
                    mail = fila["mail"]
                    if not self._mail_en_uso(mail):
                        # Reconstruimos el usuario con su rol y contraseña guardados
                        rol = Rol[fila["rol"]]
                        usuario = Usuario(
                            nombre=fila["nombre"],
                            apellido=fila["apellido"],
                            mail=mail,
                            celular=fila["celular"],
                            contrasenia=fila["contrasenia"],
                            rol=rol
                        )
                        usuario.eliminado = fila["eliminado"] == "True"
                        self.__usuarios.append(usuario)
        except Exception as e:
            print(f"Aviso: No se pudo cargar el archivo de usuarios: {e}")

    def _guardar_en_csv(self) -> None:
        """Guarda toda la lista actual de usuarios en el archivo CSV."""
        try:
            with open(ARCHIVO_CSV, mode="w", newline="", encoding="utf-8") as archivo:
                campos = ["nombre", "apellido", "mail", "celular", "contrasenia", "rol", "eliminado"]
                escritor = csv.DictWriter(archivo, fieldnames=campos)
                escritor.writeheader()
                for u in self.__usuarios:
                    escritor.writerow({
                        "nombre": u.nombre,
                        "apellido": u.apellido,
                        "mail": u.mail,
                        "celular": u.celular,
                        "contrasenia": u._Usuario__contrasenia,  # Acceso controlado a la contraseña interna
                        "rol": u.rol.name,
                        "eliminado": str(u.eliminado)
                    })
        except Exception as e:
            print(f"Error al guardar en el CSV: {e}")

    def _mail_en_uso(self, mail: str, excluir_id: int | None = None) -> bool:
        """Comprueba si el mail ya está registrado (case-insensitive)."""
        buscado = mail.strip().lower()
        return any(u.mail == buscado and u.id != excluir_id for u in self.__usuarios)

    def _validar_mail_correcto(self, mail: str) -> None:
        """Validación estricta del formato del correo electrónico."""
        mail_limpio = mail.strip()
        if not mail_limpio or "@" not in mail_limpio or "." not in mail_limpio:
            raise DatoInvalidoError("El formato del mail es incorrecto (debe contener '@' y '.')")
        
        # Validación extra opcional: que no tenga espacios internos y tenga algo antes/después del @ y del .
        partes = mail_limpio.split("@")
        if len(partes) != 2 or not partes[0] or not partes[1] or "." not in partes[1]:
            raise DatoInvalidoError("El formato del mail no es válido")

    def crear(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> Usuario:
        # 1. Validar formato correcto del mail antes de hacer nada
        self._validar_mail_correcto(mail)

        # 2. Controlar duplicados (tanto en memoria como cargados del CSV)
        if self._mail_en_uso(mail):
            raise DuplicadoError(f"El mail '{mail.strip()}' ya está registrado en el sistema")

        # 3. Crear instancia
        usuario = Usuario(nombre, apellido, mail, celular, contrasenia, rol)
        self.__usuarios.append(usuario)

        # 4. Actualizar el archivo CSV de manera persistente
        self._guardar_en_csv()

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
        usuario = self.obtener(id_usuario)
        
        if mail is not None:
            self._validar_mail_correcto(mail)
            if self._mail_en_uso(mail, usuario.id):
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
            if contrasenia is not None:
                usuario.contrasenia = contrasenia
        except Exception:
            (usuario.nombre, usuario.apellido, usuario.mail,
             usuario.celular, usuario.rol) = original
            raise

        # Guardamos cambios en el CSV
        self._guardar_en_csv()
        return usuario

    def eliminar(self, id_usuario: int, usuario_sesion: Usuario) -> None:
        usuario = self.obtener(id_usuario)
        if usuario == usuario_sesion:
            raise OperacionNoPermitidaError(
                "Un administrador no puede eliminarse a sí mismo mientras tiene la sesión iniciada"
            )
        usuario.eliminado = True
        self._guardar_en_csv()

    def autenticar(self, mail: str, contrasenia: str) -> Usuario:
        mensaje = "Mail o contraseña incorrectos"
        buscado = mail.strip().lower()
        for u in self.__usuarios:
            if u.mail == buscado:
                if u.eliminado or not u.verificar_contrasenia(contrasenia):
                    raise CredencialesInvalidasError(mensaje)
                return u
        raise CredencialesInvalidasError(mensaje)