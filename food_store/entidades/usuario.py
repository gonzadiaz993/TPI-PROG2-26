from entidades.base import Base
from enums import Rol
from excepciones import DatoInvalidoError


class Usuario(Base):
    def __init__(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> None:
        super().__init__()
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.celular = celular
        self.contrasenia = contrasenia
        self.rol = rol

    @staticmethod
    def _texto_no_vacio(valor: str, campo: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError(f"El campo '{campo}' no puede estar vacío")
        return valor.strip()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre: str = self._texto_no_vacio(valor, "nombre")

    @property
    def apellido(self) -> str:
        return self.__apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        self.__apellido: str = self._texto_no_vacio(valor, "apellido")

    @property
    def mail(self) -> str:
        return self.__mail

    @mail.setter
    def mail(self, valor: str) -> None:
        valor = self._texto_no_vacio(valor, "mail")
        if "@" not in valor or "." not in valor:
            raise DatoInvalidoError("El mail debe contener '@' y '.'")
        self.__mail: str = valor.lower()

    @property
    def celular(self) -> str:
        return self.__celular

    @celular.setter
    def celular(self, valor: str) -> None:
        self.__celular: str = self._texto_no_vacio(valor, "celular")

    # contrasenia: SIN getter; solo se puede escribir, nunca leer.
    def _set_contrasenia(self, valor: str) -> None:
        self.__contrasenia: str = self._texto_no_vacio(valor, "contraseña")

    contrasenia = property(fset=_set_contrasenia)

    @property
    def rol(self) -> Rol:
        return self.__rol

    @rol.setter
    def rol(self, valor: Rol) -> None:
        if not isinstance(valor, Rol):
            raise DatoInvalidoError("Rol inválido")
        self.__rol: Rol = valor

    def verificar_contrasenia(self, contrasenia: str) -> bool:
        return self.__contrasenia == contrasenia

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.nombre} {self.apellido} | "
            f"{self.mail} | {self.rol.name}"
        )