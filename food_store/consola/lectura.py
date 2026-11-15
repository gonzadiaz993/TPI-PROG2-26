"""Lectura validada de datos por consola.

Nunca lanza ValueError hacia afuera: ante un dato mal ingresado informa y vuelve a pedir.
Si el usuario interrumpe (Ctrl+C), lanza OperacionCanceladaError.
"""
from enum import Enum
from typing import TypeVar

import questionary
from questionary import Choice, Style

T = TypeVar("T")
E = TypeVar("E", bound=Enum)

ESTILO_ADMIN: Style = Style([
    ("pointer", "cyan bold"),
    ("highlighted", "bg:#7c3aed #ffffff bold"),
    ("text", "#9ca3af"),
    ("question", "cyan bold"),
])
ESTILO_CLIENTE: Style = Style([
    ("pointer", "green bold"),
    ("highlighted", "bg:#0284c7 fg:white bold"),
    ("text", "#9ca3af"),
    ("question", "green bold"),
])

_CONSERVAR: object = object()


class OperacionCanceladaError(Exception):
    """El usuario interrumpió (Ctrl+C) la operación en curso."""


def _input(mensaje: str) -> str:
    try:
        return input(mensaje).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        raise OperacionCanceladaError()


# ---------- Texto ----------

def pedir_texto(mensaje: str) -> str:
    """Texto obligatorio: repite hasta que no esté vacío."""
    while True:
        valor = _input(f"{mensaje}: ")
        if valor:
            return valor
        print("  ✗ El campo no puede estar vacío.")


def pedir_texto_libre(mensaje: str) -> str:
    """Texto que puede quedar vacío."""
    return _input(f"{mensaje}: ")


def pedir_texto_opcional(mensaje: str, actual: str) -> str | None:
    """Al editar: Enter conserva el valor actual (devuelve None)."""
    valor = _input(f"{mensaje} [{actual}] (Enter conserva): ")
    return valor or None


def pedir_contrasenia(mensaje: str = "Contraseña", obligatoria: bool = True) -> str:
    while True:
        valor = questionary.password(f"{mensaje}:").ask()
        if valor is None:
            raise OperacionCanceladaError()
        if valor or not obligatoria:
            return valor
        print("  ✗ La contraseña no puede estar vacía.")


# ---------- Números ----------

def pedir_entero(mensaje: str) -> int:
    while True:
        try:
            return int(_input(f"{mensaje}: "))
        except ValueError:
            print("  ✗ Ingresá un número entero válido.")


def pedir_entero_opcional(mensaje: str, actual: int | None = None) -> int | None:
    """Enter devuelve None (conservar / volver)."""
    sufijo = f" [{actual}]" if actual is not None else ""
    while True:
        valor = _input(f"{mensaje}{sufijo} (Enter conserva): " if actual is not None
                       else f"{mensaje}: ")
        if not valor:
            return None
        try:
            return int(valor)
        except ValueError:
            print("  ✗ Ingresá un número entero válido.")


def pedir_decimal(mensaje: str) -> float:
    while True:
        try:
            return float(_input(f"{mensaje}: ").replace(",", "."))
        except ValueError:
            print("  ✗ Ingresá un número válido (ej: 1500.50).")


def pedir_decimal_opcional(mensaje: str, actual: float) -> float | None:
    while True:
        valor = _input(f"{mensaje} [{actual}] (Enter conserva): ")
        if not valor:
            return None
        try:
            return float(valor.replace(",", "."))
        except ValueError:
            print("  ✗ Ingresá un número válido (ej: 1500.50).")


# ---------- Sí / No ----------

def _interpretar_si_no(valor: str) -> bool | None:
    if valor.lower() in ("s", "si", "sí"):
        return True
    if valor.lower() in ("n", "no"):
        return False
    return None


def pedir_si_no(mensaje: str) -> bool:
    while True:
        resultado = _interpretar_si_no(_input(f"{mensaje} (S/N): "))
        if resultado is not None:
            return resultado
        print("  ✗ Respondé S o N.")


def pedir_si_no_opcional(mensaje: str, actual: bool) -> bool | None:
    texto = "S" if actual else "N"
    while True:
        valor = _input(f"{mensaje} (S/N) [{texto}] (Enter conserva): ")
        if not valor:
            return None
        resultado = _interpretar_si_no(valor)
        if resultado is not None:
            return resultado
        print("  ✗ Respondé S o N.")


# ---------- Selección ----------

def elegir(mensaje: str, opciones: list[tuple[str, T]], estilo: Style | None = None) -> T:
    """Menú de selección. Devuelve el valor asociado a la opción elegida."""
    respuesta = questionary.select(
        mensaje,
        choices=[Choice(titulo, valor) for titulo, valor in opciones],
        style=estilo,
        pointer="➔",
    ).ask()
    if respuesta is None:
        raise OperacionCanceladaError()
    return respuesta


def elegir_enum(mensaje: str, enum_cls: type[E], estilo: Style | None = None) -> E:
    """Los enumerados se eligen por número, nunca escribiendo el texto."""
    opciones = [(f"{i}. {m.name}", m) for i, m in enumerate(enum_cls, start=1)]
    return elegir(mensaje, opciones, estilo)


def elegir_enum_opcional(
    mensaje: str, enum_cls: type[E], actual: E, estilo: Style | None = None
) -> E | None:
    """Igual que elegir_enum, con una opción extra para conservar el valor actual."""
    opciones: list[tuple[str, object]] = [(f"{i}. {m.name}", m) for i, m in enumerate(enum_cls, start=1)]
    opciones.append((f"0. Conservar actual ({actual.name})", _CONSERVAR))
    resultado = elegir(mensaje, opciones, estilo)
    return None if resultado is _CONSERVAR else resultado  # type: ignore[return-value]
