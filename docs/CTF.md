# Guía del CTF — LabShop

## Vulnerabilidad 1 — Escalada de privilegios mediante API

La interfaz web de perfil **no contiene un campo para cambiar `role`**. El atributo existe en la base de datos y se utiliza para controlar el acceso al panel `/technician`, pero la modificación privilegiada se ha dejado en una API no enlazada desde la interfaz.

Endpoint:

```text
POST /api/user/update
```

La vulnerabilidad es de **mass assignment / autorización insuficiente**: el servidor acepta `role` desde el cliente y no verifica que el usuario autenticado tenga permiso para modificar ese atributo.

### Objetivo

Partiendo de una cuenta `customer`, descubrir la API y conseguir que su rol pase a `technician`.

### Comprobación del impacto

Una vez modificado el rol, acceder a:

```text
/technician
```

El panel muestra datos ficticios de todos los usuarios del laboratorio.

## Vulnerabilidad 2 — SQL injection desde la búsqueda

La búsqueda de productos utiliza directamente el parámetro `q` para construir un script SQL.

Endpoint:

```text
GET /products/search?q=...
```

La aplicación ejecuta conceptualmente:

```sql
SELECT * FROM products WHERE name LIKE '%VALOR_DEL_USUARIO%'
```

pero de forma insegura mediante `executescript()`. Por ello, una entrada de búsqueda especialmente construida puede cerrar la cadena SQL y añadir otra sentencia.

### Payload de laboratorio

Para cambiar a `0` el precio del producto con ID `1`:

```text
'; UPDATE products SET price=0 WHERE id=1; --
```

La petición puede hacerse desde la propia barra de búsqueda, codificando los caracteres especiales si el navegador los transforma en la URL.

Después, comprobar el resultado en:

```text
/
```

o en:

```text
/admin/products
```

El precio habrá quedado persistido en `lab.db`.

### Qué demuestra

- La entrada de búsqueda llega directamente al intérprete SQL.
- Es posible cerrar la cadena de la consulta original.
- `executescript()` permite ejecutar una segunda sentencia.
- La sentencia adicional puede modificar datos persistentes.

## Reinicio

Detener Flask, borrar `lab.db` y ejecutar de nuevo `python app.py`.
