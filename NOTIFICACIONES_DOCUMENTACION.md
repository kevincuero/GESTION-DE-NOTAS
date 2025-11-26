# 📢 SISTEMA DE NOTIFICACIONES - DOCUMENTACIÓN COMPLETA

## Resumen del Proyecto

Se ha implementado un sistema completo de notificaciones en la plataforma de gestión de estudiantes que permite la comunicación bidireccional entre profesores y estudiantes a través de la base de datos.

---

## 🏗️ CAMBIOS EN LA BASE DE DATOS

### Tabla `notificaciones` (Mejorada)

```sql
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    INDEX idx_estudiante (id_estudiante),
    INDEX idx_profesor (id_profesor),
    INDEX idx_leida (leida)
);
```

**Cambios realizados:**
- ✅ Agregado campo `id_profesor` para relacionar la notificación con quien la envía
- ✅ Mejorado campo `leida` (BOOLEAN) para marcar si fue leída
- ✅ Agregados índices para optimizar consultas
- ✅ Agregada columna `fecha` con TIMESTAMP automático

---

## 📁 ARCHIVOS MODIFICADOS Y CREADOS

### 1. **Models/notificacion.py** (Mejora)

**Métodos disponibles:**

```python
# Crear notificaciones
Notificacion.crear(id_estudiante, id_profesor, titulo, mensaje)
Notificacion.crear_multiples(id_estudiantes, id_profesor, titulo, mensaje)

# Obtener notificaciones
Notificacion.obtener_por_estudiante(id_estudiante, leidas=None)
Notificacion.obtener_por_id(id_notificacion)
Notificacion.obtener_por_profesor(id_profesor)

# Marcar como leídas
Notificacion.marcar_como_leida(id_notificacion)
Notificacion.marcar_multiples_como_leidas(id_notificaciones)
Notificacion.marcar_todas_como_leidas(id_estudiante)

# Gestión
Notificacion.eliminar(id_notificacion)
Notificacion.obtener_no_leidas_count(id_estudiante)
```

### 2. **Controllers/notificacion_controller.py** (NUEVO)

Controlador centralizado para todas las operaciones de notificaciones.

**Métodos principales:**

```python
NotificacionController.enviar_notificacion_a_estudiante()
NotificacionController.enviar_notificacion_a_multiples()
NotificacionController.enviar_notificacion_a_clase()
NotificacionController.obtener_notificaciones_estudiante()
NotificacionController.obtener_notificaciones_sin_leer()
NotificacionController.marcar_como_leida()
NotificacionController.marcar_todas_como_leidas()
NotificacionController.obtener_conteo_no_leidas()
NotificacionController.eliminar_notificacion()
NotificacionController.obtener_notificaciones_profesor()
```

### 3. **main.py** (Actualización)

#### Rutas de Profesor:

```python
# Enviar notificación (mejorada con tabs)
@app.route('/profesor/enviar_notificacion', methods=['GET', 'POST'])
def enviar_notificacion()

# Enviar a toda la clase
@app.route('/profesor/enviar_notificacion_grupo', methods=['POST'])
def enviar_notificacion_grupo()
```

#### APIs para Estudiante:

```python
# Marcar como leída
@app.route('/api/notificacion/marcar_leida/<int:id_notificacion>', methods=['POST'])
def api_marcar_notificacion_leida()

# Marcar todas como leídas
@app.route('/api/notificacion/marcar_todas_leidas', methods=['POST'])
def api_marcar_todas_notificaciones_leidas()

# Eliminar notificación
@app.route('/api/notificacion/eliminar/<int:id_notificacion>', methods=['DELETE'])
def api_eliminar_notificacion()

# Obtener conteo de no leídas
@app.route('/api/notificacion/sin_leer', methods=['GET'])
def api_notificaciones_sin_leer()
```

#### Ruta Estudiante:

```python
# Ver notificaciones
@app.route('/estudiante/notificaciones')
def notificaciones_estudiante()
```

### 4. **Views/profesor/EnviarNotificacion.html** (Renovada)

**Nuevas características:**

- 📌 Sistema de TABS (Individual / A toda la clase)
- 👤 Envío a estudiante individual
- 👥 Envío masivo a toda la clase
- 📝 Interfaz mejorada con estilos modernos
- ⚙️ Validación en tiempo real
- 📢 Mensajes de confirmación

**Funcionalidades:**
- Selección dinámica de estudiantes por materia
- Validación de campos obligatorios
- Alertas de éxito/error

### 5. **Views/estudiante/mis_notificaciones.html** (Renovada)

**Nuevas características:**

- 📋 Lista de todas las notificaciones
- ✅ Filtro: Todas / Solo no leídas
- 🔵 Indicador visual de notificaciones nuevas
- 📛 Badge con contador de no leídas
- ⏰ Fecha y hora de cada notificación
- 👨‍🏫 Nombre del profesor remitente
- 🔄 Marcar como leída (individual o masivo)
- 🗑️ Eliminar notificaciones
- 💾 Estado persistente en BD

---

## 🔄 FLUJO DE COMUNICACIÓN

```
PROFESOR
   ↓
[Enviar Notificación]
   ↓
[NotificacionController]
   ↓
[Models/Notificacion - Crear]
   ↓
[Base de Datos - Tabla notificaciones]
   ↓
[ESTUDIANTE]
[Ver Notificaciones - mis_notificaciones.html]
   ↓
[Marcar como Leída / Eliminar]
   ↓
[APIs - Update/Delete]
   ↓
[Base de Datos - Update]
```

---

## 📊 ESTRUCTURA DE DATOS

### Tabla notificaciones

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | Identificador único |
| id_estudiante | INT | FK a estudiantes |
| id_profesor | INT | FK a profesores (remitente) |
| titulo | VARCHAR(255) | Asunto de la notificación |
| mensaje | TEXT | Contenido del mensaje |
| leida | BOOLEAN | Estado de lectura |
| fecha | TIMESTAMP | Fecha/hora de creación |

---

## 🚀 CÓMO USAR

### Para PROFESORES:

#### 1. **Enviar notificación individual:**
```
1. Ir a: /profesor/enviar_notificacion
2. Seleccionar materia
3. Seleccionar estudiante
4. Escribir título y mensaje
5. Hacer clic en "Enviar Notificación"
```

#### 2. **Enviar a toda la clase:**
```
1. Ir a: /profesor/enviar_notificacion
2. Ir al tab "A Toda la Clase"
3. Seleccionar materia
4. Escribir título y mensaje
5. Hacer clic en "Enviar a Toda la Clase"
```

### Para ESTUDIANTES:

#### 1. **Ver notificaciones:**
```
1. Ir a: /estudiante/notificaciones
2. Ver lista de notificaciones
3. Filtrar por "No Leídas" si desea
```

#### 2. **Marcar como leída:**
```
1. Hacer clic en "Marcar como leída" en la notificación
2. La notificación se marca como leída
```

#### 3. **Marcar todas como leídas:**
```
1. Hacer clic en "Marcar todas como leídas"
2. Confirmar la acción
```

#### 4. **Eliminar notificación:**
```
1. Hacer clic en "Eliminar"
2. Confirmar la eliminación
```

---

## 💻 EJEMPLOS DE CÓDIGO

### Enviar notificación a un estudiante:

```python
from Controllers.notificacion_controller import NotificacionController

resultado = NotificacionController.enviar_notificacion_a_estudiante(
    id_estudiante=1,
    id_profesor=1,
    titulo="Nueva tarea disponible",
    mensaje="Se ha publicado la tarea 3 de Matemáticas para el próximo viernes."
)

if resultado['success']:
    print(resultado['message'])  # "Notificación enviada correctamente."
```

### Enviar a toda una clase:

```python
resultado = NotificacionController.enviar_notificacion_a_clase(
    id_materia=1,
    id_profesor=1,
    titulo="Importante: Cambio de horario",
    mensaje="La clase de mañana se trasladará a las 2:00 PM."
)

print(f"Enviadas a {resultado['count']} estudiantes")
```

### Obtener notificaciones no leídas:

```python
notificaciones = NotificacionController.obtener_notificaciones_sin_leer(
    id_estudiante=1
)

for notif in notificaciones:
    print(f"{notif['titulo']} - {notif['profesor_nombre']}")
```

### Marcar como leída:

```python
resultado = NotificacionController.marcar_como_leida(id_notificacion=1)
```

---

## 🔐 SEGURIDAD

✅ **Validaciones implementadas:**
- Verificación de rol de usuario
- Validación de permisos por sesión
- Sanitización de datos de entrada
- Uso de prepared statements para prevenir SQL injection
- Validación de relaciones (profesor-estudiante-materia)

---

## 📈 CARACTERÍSTICAS FUTURAS (Opcionales)

- 📧 Integración con correo electrónico
- 🔔 Notificaciones push
- 📱 App móvil para notificaciones
- 🏷️ Categorización de notificaciones
- 📌 Notificaciones fijadas
- 🔍 Búsqueda de notificaciones
- 📊 Estadísticas de lectura
- ⏰ Programación de notificaciones

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Actualizar tabla `notificaciones` en BD
- [x] Mejorar Model `Notificacion.py`
- [x] Crear `NotificacionController.py`
- [x] Agregar rutas en `main.py`
- [x] Crear APIs REST para notificaciones
- [x] Actualizar vista profesor (`EnviarNotificacion.html`)
- [x] Actualizar vista estudiante (`mis_notificaciones.html`)
- [x] Implementar filtros de notificaciones
- [x] Marcar como leída (individual y masivo)
- [x] Eliminar notificaciones
- [x] Validación de permisos
- [x] Respuestas JSON en APIs

---

## 📝 NOTAS IMPORTANTES

1. **Base de datos:** Ejecutar el script `GestionEstduiante.sql` para actualizar la tabla
2. **Sesiones:** El sistema verifica que el usuario esté autenticado
3. **Roles:** Solo profesores pueden enviar, solo estudiantes pueden recibir
4. **Estado de lectura:** Se mantiene en BD para persistencia
5. **Eliminación:** Las notificaciones pueden ser eliminadas por el estudiante

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Problema: Las notificaciones no se envían
**Solución:** Verificar que la tabla `notificaciones` tenga los campos correctos incluido `id_profesor`

### Problema: Error al marcar como leída
**Solución:** Verificar que el cookie de sesión esté activo

### Problema: No se ven notificaciones en la tabla
**Solución:** Ejecutar migración de BD para actualizar el esquema

---

## 👨‍💻 AUTOR
Sistema de Notificaciones - Proyecto Final Gestión de Estudiantes

---

**Versión:** 1.0  
**Última actualización:** Noviembre 2025  
**Estado:** ✅ Funcional y probado
