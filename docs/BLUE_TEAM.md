# Blue Team — LabShop

## Escalada de privilegios

Indicadores:
- POST a `/api/user/update`.
- Cambios del atributo `role`.
- Cambio de `customer` a `technician`.
- Acceso posterior a `/technician`.

Mitigaciones:
- No aceptar `role` desde entradas controladas por el cliente.
- Separar DTOs de actualización de perfil y atributos administrativos.
- Comprobar autorización en servidor.
- Registrar cambios de roles.
- Aplicar mínimo privilegio.

## SQL injection / modificación de precios

Indicadores:
- Peticiones a `/products/search` con caracteres de cierre de cadenas SQL.
- Errores SQL en búsquedas.
- Consultas que contienen `UPDATE`, `INSERT`, `DELETE` o comentarios SQL procedentes de parámetros de búsqueda.
- Cambios inesperados de precios.

Mitigaciones:
- Consultas parametrizadas.
- No utilizar `executescript()` con datos procedentes del usuario.
- Validar y normalizar parámetros.
- Autenticar y autorizar cualquier operación de modificación.
- Registrar cambios de precios.
- Alertar ante patrones de SQL injection.
