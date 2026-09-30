# CTF Laboratorio Shop

Laboratorio académico deliberadamente vulnerable para ejecutarse de forma local.

## Requisitos

- Python 3.11+ recomendado
- Visual Studio Code
- Navegador web

## Instalación

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`.

La aplicación solo escucha en `127.0.0.1`.

## Usuarios

| Usuario | Contraseña | Rol inicial |
|---|---|---|
| alice | alice123 | customer |
| bruno | bruno123 | customer |
| carla | carla123 | customer |
| tecnico | tecnico123 | technician |

Todos los datos son ficticios y están destinados exclusivamente al laboratorio.

## Vulnerabilidad 1 — Escalada mediante API

El formulario de perfil ya **no permite modificar el rol**.

La vulnerabilidad se encuentra únicamente en la API no enlazada desde la interfaz:

```text
POST /api/user/update
```

El endpoint acepta `role` desde el cliente y no comprueba que el usuario tenga autorización para cambiarlo. Esto permite demostrar una vulnerabilidad de mass assignment / autorización insuficiente.

El impacto se comprueba accediendo a `/technician` después de que una cuenta `customer` haya sido convertida en `technician`.

## Vulnerabilidad 2 — SQL injection desde la búsqueda

La búsqueda:

```text
GET /products/search?q=...
```

es deliberadamente vulnerable. El parámetro `q` se incorpora a un script SQL y se ejecuta con `executescript()`.

Payload de laboratorio para cambiar el precio del producto `1` a cero:

```text
'; UPDATE products SET price=0 WHERE id=1; --
```

Después se puede verificar el cambio en la portada o en `/admin/products`.

## OSINT

Las rutas `/osint`, `/social/reddit` y `/social/x` contienen perfiles completamente simulados. No se utilizan cuentas reales.

## Restaurar la base de datos

Detén Flask, elimina `lab.db` y vuelve a ejecutar:

```bash
python app.py
```

La base de datos se recreará con los valores iniciales.

## Evidencias recomendadas

- Reconocimiento de rutas/endpoints.
- Capturas de las pistas OSINT.
- Peticiones HTTP relevantes.
- Cambio de rol y acceso posterior al panel técnico.
- Payload de búsqueda utilizado para la SQL injection.
- Precio antes y después.
- Evidencia de persistencia tras recargar.

## Defensas

- Autorización en servidor para cambios de roles.
- DTOs que no expongan atributos administrativos.
- Consultas SQL parametrizadas.
- No usar `executescript()` con entradas del usuario.
- Autenticación y autorización en APIs administrativas.
- Registro de cambios sensibles.
- Mínimo privilegio.
- No almacenar tarjetas completas en texto plano en un sistema real.
