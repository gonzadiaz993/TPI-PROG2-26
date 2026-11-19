# integrantes 
# - Astargo Leonardo Legajo: 54195
# - Diaz Gonzalo Legajo: 54212
# Food Store – TPI Programación II (UTN – TUP a Distancia)

Sistema de gestión de pedidos de comida por consola, hecho con POO en Python.

## Requisitos

- Python 3.12 o superior
- Biblioteca `questionary` (menús con flechas): `pip install -r requirements.txt`

## Cómo ejecutar

```bash
cd food_store
python main.py
```

Pruebas del modelo y los servicios (sin menú):

```bash
cd food_store
python pruebas.py
```

## Credenciales iniciales

| Rol | Mail | Contraseña |
|---|---|---|
| ADMIN | admin@foodstore.com | admin123 |
| USUARIO | juan@foodstore.com | 123 |

Los usuarios se guardan en `food_store/usuarios.csv` (categorías, productos y pedidos viven en memoria).
Para reiniciar los usuarios, borrar ese archivo: se vuelve a crear con los datos iniciales.

## Estructura

```
food_store/
├── main.py          # crea los servicios y arranca el menú
├── pruebas.py       # pruebas del modelo y servicios
├── entidades/       # clases del UML (Base, Categoria, Producto, Usuario, Pedido, DetallePedido, Calculable)
├── enums/           # Rol, Estado, FormaPago
├── excepciones/     # FoodStoreError y subclases
├── servicios/       # lógica de negocio y colecciones
└── consola/         # Menu, MenuAdministrador, MenuCliente, login y lectura validada
```

## Enlaces

- Video de demostración: https://youtu.be/OGbabwdAGV4?si=VdWIcgREgYcZKAZn
- Repositorio GitHub: https://github.com/gonzadiaz993/TPI-PROG2-26.git
