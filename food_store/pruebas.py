from entidades import Categoria, Producto, Usuario, Pedido
from enums import Rol, FormaPago
from excepciones import FoodStoreError

cat = Categoria("Pizzas", "Pizzas al horno")
pizza = Producto("Muzzarella", 5000.0, 10, cat)
user = Usuario("Ana", "Pérez", "ana@foodstore.com", "261555", "1234", Rol.USUARIO)

pedido = Pedido(user, FormaPago.EFECTIVO)
pedido.agregar_detalle(2, pizza)
pedido.agregar_detalle(1, pizza)   # suma al detalle existente
print(pedido, "->", pedido.detalles[0])
print("Contraseña OK:", user.verificar_contrasenia("1234"))

try:
    pedido.agregar_detalle(50, pizza)
except FoodStoreError as e:
    print("Error esperado:", e)

try:
    print(user.contrasenia)
except AttributeError:
    print("Error esperado: la contraseña no se puede leer")



#---------------------------------------------------------------------------------------------------------------------------------------
from enums import Rol, Estado, FormaPago
from excepciones import FoodStoreError
from servicios import CategoriaServicio, ProductoServicio, UsuarioServicio, PedidoServicio

cats = CategoriaServicio()
prods = ProductoServicio(cats)
users = UsuarioServicio()
pedidos = PedidoServicio(users, prods)

admin = users.crear("Ana", "Pérez", "admin@foodstore.com", "261555", "admin123", Rol.ADMIN)
cliente = users.crear("Juan", "Gómez", "juan@mail.com", "261444", "1234", Rol.USUARIO)
cat = cats.crear("Pizzas", "Pizzas al horno")
pizza = prods.crear("Muzzarella", "Clásica", 5000.0, 10, "", True, cat.id)

def intentar(descripcion, funcion):
    try:
        resultado = funcion()
        print(f"OK     {descripcion}: {resultado}")
    except FoodStoreError as e:
        print(f"ERROR  {descripcion}: {e}")

intentar("login correcto", lambda: users.autenticar("admin@foodstore.com", "admin123"))
intentar("login incorrecto", lambda: users.autenticar("admin@foodstore.com", "mala"))
intentar("categoría duplicada", lambda: cats.crear("PIZZAS", "otra"))
intentar("mail duplicado", lambda: users.crear("X", "Y", "JUAN@mail.com", "1", "1", Rol.USUARIO))
intentar("admin se elimina a sí mismo", lambda: users.eliminar(admin.id, admin))
intentar("eliminar categoría con productos", lambda: cats.eliminar(cat.id, prods))

p = pedidos.crear_pedido(cliente.id, FormaPago.EFECTIVO, [(pizza.id, 4)])
print("Pedido:", p, "| stock pizza:", pizza.stock)          # 6
intentar("pedido sin stock", lambda: pedidos.crear_pedido(cliente.id, FormaPago.TARJETA, [(pizza.id, 99)]))
print("Stock intacto tras el fallo:", pizza.stock)          # 6

intentar("PENDIENTE → TERMINADO", lambda: pedidos.actualizar(p.id, estado=Estado.TERMINADO))
intentar("PENDIENTE → CANCELADO", lambda: pedidos.actualizar(p.id, estado=Estado.CANCELADO))
print("Stock devuelto:", pizza.stock)                       # 10
intentar("CANCELADO → CONFIRMADO", lambda: pedidos.actualizar(p.id, estado=Estado.CONFIRMADO))