# 📢 SISTEMA DE NOTIFICACIONES - GUÍA DE IMPLEMENTACIÓN

## ⚡ Inicio Rápido

### 1. Actualizar Base de Datos

```sql
-- Ejecutar en tu cliente MySQL:
mysql -u root -p GestionDeEstudiantes < Database/actualizar_notificaciones.sql
```

### 2. Verificar la Instalación

```bash
cd Campus
python test_notificaciones.py
```

### 3. Usar el Sistema

**Como Profesor:**
- Ir a: `http://localhost:5000/profesor/enviar_notificacion`
- Elegir entre:
  - 👤 Enviar a estudiante individual
  - 👥 Enviar a toda la clase

**Como Estudiante:**
- Ir a: `http://localhost:5000/estudiante/notificaciones`
- Ver todas las notificaciones
- Filtrar por no leídas
- Marcar como leída
- Eliminar

---

## 📦 Archivos Modificados/Creados

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `Database/GestionEstduiante.sql` | Modificado | Tabla notificaciones mejorada |
| `Database/actualizar_notificaciones.sql` | NUEVO | Script de migración |
| `Models/notificacion.py` | Mejorado | Métodos completos |
| `Controllers/notificacion_controller.py` | NUEVO | Controlador centralizado |
| `Views/profesor/EnviarNotificacion.html` | Renovada | UI con tabs y validación |
| `Views/estudiante/mis_notificaciones.html` | Renovada | Interfaz mejorada |
| `main.py` | Actualizado | Nuevas rutas y APIs |
| `test_notificaciones.py` | NUEVO | Suite de pruebas |
| `NOTIFICACIONES_DOCUMENTACION.md` | NUEVO | Documentación completa |

---

## 🔑 Características Principales

### ✅ Para Profesores

- [x] Enviar notificaciones individuales a estudiantes
- [x] Enviar a toda una clase de una vez
- [x] Selección dinámica de estudiantes
- [x] Título y mensaje personalizados
- [x] Historial de notificaciones enviadas
- [x] Ver estudiantes inscritos

### ✅ Para Estudiantes

- [x] Ver todas las notificaciones recibidas
- [x] Filtrar notificaciones (todas / no leídas)
- [x] Indicador visual de notificaciones nuevas
- [x] Marcar como leída (individual o en lote)
- [x] Eliminar notificaciones
- [x] Ver nombre del profesor remitente
- [x] Ver fecha y hora exacta

### ✅ Base de Datos

- [x] Relación profesor-estudiante por notificación
- [x] Estado de lectura persistente
- [x] Índices para optimizar consultas
- [x] Timestamps automáticos
- [x] Eliminación en cascada

---

## 🛠️ APIs REST Disponibles

### Marcar Notificación como Leída

```bash
POST /api/notificacion/marcar_leida/<id_notificacion>
```

**Response:**
```json
{
  "success": true,
  "message": "Notificación marcada como leída."
}
```

### Marcar Todas como Leídas

```bash
POST /api/notificacion/marcar_todas_leidas
```

### Eliminar Notificación

```bash
DELETE /api/notificacion/eliminar/<id_notificacion>
```

### Obtener Conteo de No Leídas

```bash
GET /api/notificacion/sin_leer
```

**Response:**
```json
{
  "count": 5
}
```

---

## 💡 Ejemplos de Uso

### Desde Python (Backend)

```python
from Controllers.notificacion_controller import NotificacionController

# Enviar a un estudiante
NotificacionController.enviar_notificacion_a_estudiante(
    id_estudiante=1,
    id_profesor=1,
    titulo="Nueva tarea",
    mensaje="Completa los ejercicios 1-10"
)

# Enviar a toda la clase
NotificacionController.enviar_notificacion_a_clase(
    id_materia=1,
    id_profesor=1,
    titulo="Cambio de horario",
    mensaje="La clase de mañana será a las 2:00 PM"
)

# Obtener notificaciones
notificaciones = NotificacionController.obtener_notificaciones_sin_leer(1)
```

### Desde JavaScript (Frontend)

```javascript
// Marcar como leída
fetch(`/api/notificacion/marcar_leida/1`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => console.log(data.message));

// Obtener no leídas
fetch('/api/notificacion/sin_leer')
    .then(r => r.json())
    .then(data => console.log(`${data.count} sin leer`));
```

---

## 📊 Estructura de Base de Datos

```sql
notificaciones
├── id (PK)
├── id_estudiante (FK)
├── id_profesor (FK)
├── titulo
├── mensaje
├── leida (BOOLEAN)
├── fecha (TIMESTAMP)
├── idx_estudiante
├── idx_profesor
└── idx_leida
```

---

## ✨ Mejoras Implementadas

### Modelo (notificacion.py)

```python
✅ Crear una notificación
✅ Crear múltiples notificaciones
✅ Obtener por estudiante (con filtro leida/no leida)
✅ Obtener por ID
✅ Obtener por profesor
✅ Marcar como leída
✅ Marcar múltiples como leída
✅ Marcar todas como leída
✅ Eliminar
✅ Contar no leídas
```

### Vistas

#### Profesor (EnviarNotificacion.html)
```
[TABS]
├─ Individual
│  ├─ Seleccionar Materia
│  ├─ Seleccionar Estudiante
│  ├─ Título
│  └─ Mensaje
└─ A Toda la Clase
   ├─ Seleccionar Materia
   ├─ Título
   └─ Mensaje
```

#### Estudiante (mis_notificaciones.html)
```
[CONTROLES]
├─ Filtro: Todas
├─ Filtro: No Leídas (con badge)
└─ Marcar Todas como Leídas

[NOTIFICACIÓN]
├─ Estado (NUEVA/LEÍDA)
├─ Título
├─ Profesor
├─ Mensaje
├─ Fecha
├─ Acciones (Marcar leída / Eliminar)
```

---

## 🧪 Pruebas

### Ejecutar Suite Completa

```bash
python test_notificaciones.py
```

**Pruebas Incluidas:**
1. ✅ Crear notificación individual
2. ✅ Crear múltiples notificaciones
3. ✅ Obtener notificaciones
4. ✅ Obtener sin leer
5. ✅ Contar no leídas
6. ✅ Marcar como leída
7. ✅ Marcar todas como leídas
8. ✅ Obtener por profesor
9. ✅ Enviar a clase
10. ✅ Verificar BD

---

## 🔒 Seguridad

### Validaciones

- ✅ Verificación de rol de usuario
- ✅ Validación de sesión
- ✅ Prepared statements (sin SQL injection)
- ✅ Sanitización de input
- ✅ Validación de relaciones

### Permisos

- Solo profesores pueden enviar notificaciones
- Solo estudiantes pueden recibirlas
- Solo el propietario puede marcar como leída

---

## 📝 Notas Importantes

1. **Base de Datos**: Ejecutar migración antes de usar
2. **Sesión**: Usuario debe estar autenticado
3. **Relaciones**: Validar profesor-materia-estudiante
4. **Estado**: Persistente en BD
5. **Eliminación**: No recuperable

---

## 🚀 Próximas Mejoras

- [ ] Correo electrónico automático
- [ ] Notificaciones push
- [ ] Búsqueda y filtros avanzados
- [ ] Notificaciones programadas
- [ ] Estadísticas de lectura
- [ ] Categorización por tema

---

## ❓ Preguntas Frecuentes

**P: ¿Se envían correos electrónicos?**
R: No actualmente. Solo notificaciones en plataforma. Puede agregarse después.

**P: ¿Las notificaciones son en tiempo real?**
R: Se guardan inmediatamente en BD. Para actualización en vivo, agregar WebSockets.

**P: ¿Se pueden recuperar notificaciones eliminadas?**
R: No, la eliminación es permanente. Considerar implementar soft delete.

**P: ¿Hay límite de notificaciones?**
R: No, pero se recomienda archivar antiguas periódicamente.

---

## 📞 Soporte

Para reportar bugs o solicitar features:
1. Revisar `NOTIFICACIONES_DOCUMENTACION.md`
2. Ejecutar `test_notificaciones.py`
3. Revisar logs de Flask

---

**¡Sistema de Notificaciones Implementado Exitosamente! ✅**
