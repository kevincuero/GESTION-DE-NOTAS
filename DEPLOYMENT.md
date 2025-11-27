# Despliegue y conexión a base de datos

Este proyecto usa MySQL en producción y localmente puedes usar XAMPP + HeidiSQL.
A continuación se indican instrucciones para que la aplicación funcione en local y en Render (u otro PaaS).

---

## Concepto importante
- Si estás usando XAMPP en tu máquina local (localhost), servicios externos como Render **no** podrán conectarse a tu MySQL local por seguridad/redes.
- Para desplegar en Render debes usar una base de datos accesible desde Internet (por ejemplo RDS, PlanetScale, ClearDB, o un servidor MySQL con IP pública y reglas de firewall abiertas).

---

## Variables de entorno necesarias
Configurar estas variables en Render (o en tu entorno local `.env` para desarrollo):

- `DB_HOST` — host del servidor MySQL (ej: `db.example.com` o `127.0.0.1` para local XAMPP)
- `DB_PORT` — puerto (por defecto `3306`)
- `DB_USER` — usuario MySQL
- `DB_PASSWORD` — contraseña
- `DB_NAME` — nombre de la base de datos (ej: `GestionDeEstudiantes`)

Opcionalmente para OAuth u otros servicios:
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

---

## Despliegue en Render (resumen)
1. Crear o provisionar una base de datos MySQL accesible desde Internet.
2. En el servicio de Render, en la sección Environment → Environment Variables, añadir las variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` con los valores de tu base de datos remota.
3. En `Start Command` usar: `gunicorn --workers 4 --bind 0.0.0.0:$PORT main:app`
4. Hacer deploy (puede ser automatico desde GitHub). Verifica la URL `https://<tu-servicio>/ _health` para comprobar estado (`/ _health` sin espacio).

---

## Desarrollo local con XAMPP + HeidiSQL
1. Inicia Apache y MySQL en el panel de XAMPP.
2. Abre HeidiSQL y conecta con `127.0.0.1:3306` (usuario `root` u otro que tengas configurado).
3. Crear la BD `GestionDeEstudiantes` y ejecutar los scripts SQL en el directorio `Database/` si aún no existen tablas.
4. Crear un archivo `.env` en la raíz del proyecto con:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=GestionDeEstudiantes
```

5. Ejecutar la app localmente (por ejemplo `python main.py` o con Flask dev server).

---

## Qué ha cambiado en el código
- `Config/database_connection.py` ahora:
  - Intenta conectar a MySQL con reintentos.
  - Si no puede conectar, devuelve una `NullConnection` para que la aplicación no falle y funcione en modo degradado (no lanza excepciones por falta de BD).
  - Imprime mensajes claros con los valores de conexión usados y el error.
- Se añadió el endpoint `/ _health` en `main.py` que devuelve el estado de la app y si la BD está accesible.

> Nota: usar `NullConnection` evita que la app crashee en entornos donde no exista la BD (por ejemplo Render sin variables). Sin embargo, para que la aplicación sea totalmente funcional (crear usuarios, operaciones con tablas), necesitas una base de datos MySQL real configurada y accesible.

---

## Recomendación final
- Para producción en Render, provisiona un servicio de MySQL (por ejemplo RDS, PlanetScale, ClearDB) y configura las variables de entorno en Render.
- Alternativamente para pruebas rápidas en la nube, puedes migrar la app a usar SQLite en producción, pero requiere adaptar las consultas (placeholders) y la lógica: actualmente la app asume MySQL.

Si quieres, puedo:
- Añadir una ruta /debug para ver valores de variables de entorno (con protección),
- O añadir una opción para usar SQLite en modo `DEV_SQLITE=true` (haría cambios puntuales en consultas para compatibilidad).

Dime cuál de esas opciones prefieres y lo implemento.
