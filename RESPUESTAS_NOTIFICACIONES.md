# 💬 Sistema de Respuestas en Notificaciones

## 📋 Descripción General

Se ha implementado un sistema completo de mensajería bidireccional que permite a los estudiantes:
- **Ver el mensaje completo** del profesor en un modal expandido
- **Responder** directamente a las notificaciones
- **Tener conversaciones** con profesores por materia
- **Marcar mensajes** como leídos

## 🗂️ Cambios Realizados

### 1. 🗄️ Base de Datos (`Database/GestionEstduiante.sql`)

**Nueva tabla `mensajes`** para almacenar conversaciones:

```sql
CREATE TABLE IF NOT EXISTS mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_notificacion INT NOT NULL,           -- Referencia a notificación original
    id_estudiante INT NOT NULL,              -- Estudiante en conversación
    id_profesor INT NOT NULL,                -- Profesor en conversación
    id_materia INT,                          -- Materia del contexto
    remitente_tipo ENUM('estudiante', 'profesor') NOT NULL,
    contenido TEXT NOT NULL,                 -- Contenido del mensaje
    leido BOOLEAN DEFAULT FALSE,             -- Estado de lectura
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_notificacion) REFERENCES notificaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE SET NULL,
    INDEX idx_notificacion (id_notificacion),
    INDEX idx_estudiante_profesor (id_estudiante, id_profesor),
    INDEX idx_leido (leido),
    INDEX idx_fecha (fecha)
);
```

**Características:**
- ✅ Almacena mensajes/respuestas a notificaciones
- ✅ Identifica si el remitente es estudiante o profesor
- ✅ Vinculado a materias para contexto académico
- ✅ Optimizado con índices para consultas rápidas

---

### 2. 📦 Modelo (`Models/mensaje.py`) - NUEVO

**Métodos disponibles:**

| Método | Descripción |
|--------|-------------|
| `crear()` | Crea un nuevo mensaje de respuesta |
| `obtener_por_notificacion()` | Obtiene todos los mensajes de una notificación |
| `obtener_conversacion()` | Obtiene conversación completa estudiante-profesor |
| `marcar_como_leido()` | Marca un mensaje como leído |
| `obtener_no_leidos_count()` | Cuenta mensajes no leídos |
| `obtener_profesores_conversacion()` | Lista profesores con conversaciones activas |
| `eliminar()` | Elimina un mensaje |

**Ejemplo de uso:**

```python
from Models.mensaje import Mensaje

# Crear un mensaje de respuesta
mensaje_id = Mensaje.crear(
    id_notificacion=1,
    id_estudiante=5,
    id_profesor=3,
    id_materia=2,
    remitente_tipo='estudiante',
    contenido="Gracias por la retroalimentación"
)

# Obtener conversación
conversacion = Mensaje.obtener_conversacion(id_estudiante=5, id_profesor=3)
```

---

### 3. 🎮 Controlador (`Controllers/mensaje_controller.py`) - NUEVO

**Métodos disponibles:**

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `enviar_respuesta()` | Envía respuesta a notificación | `{success, message, mensaje_id}` |
| `obtener_mensajes_notificacion()` | Lista mensajes de una notificación | `list` |
| `obtener_conversacion()` | Obtiene conversación estudiante-profesor | `list` |
| `marcar_como_leido()` | Marca mensaje como leído | `{success, message}` |
| `obtener_profesores_con_conversacion()` | Lista profesores activos | `list` |
| `obtener_notificacion_con_detalles()` | Notificación + mensajes | `dict` |
| `enviar_mensaje_inicial()` | Inicia conversación nueva | `{success, message, notificacion_id}` |

**Ejemplo:**

```python
from Controllers.mensaje_controller import MensajeController

resultado = MensajeController.enviar_respuesta(
    id_notificacion=1,
    id_estudiante=5,
    id_profesor=3,
    id_materia=2,
    contenido="Mi pregunta sobre el tema..."
)

print(resultado)
# {'success': True, 'message': 'Respuesta enviada correctamente.', 'mensaje_id': 42}
```

---

### 4. 🛣️ Rutas (`main.py`) - NUEVAS

#### **GET/POST `/estudiante/notificaciones`**
Carga página de notificaciones del estudiante.

#### **GET `/api/notificacion/<id>`**
Obtiene detalles de una notificación con conversación.

**Respuesta:**
```json
{
  "success": true,
  "notificacion": {
    "id": 1,
    "titulo": "Retroalimentación de tarea",
    "mensaje": "Tu tarea necesita más análisis...",
    "profesor_nombre": "Dr. García",
    "fecha": "2025-11-14 10:30:00"
  },
  "mensajes": [
    {
      "id": 1,
      "remitente_tipo": "profesor",
      "remitente_nombre": "Dr. García",
      "contenido": "Texto del mensaje...",
      "fecha": "2025-11-14 10:30:00"
    }
  ]
}
```

#### **POST `/api/notificacion/<id>/responder`**
Envía respuesta a una notificación.

**Body:**
```json
{
  "contenido": "Tu respuesta aquí",
  "id_profesor": 3,
  "id_materia": 2
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Respuesta enviada correctamente.",
  "mensaje_id": 42
}
```

#### **GET `/api/estudiante/materias`**
Obtiene materias inscritas del estudiante.

**Respuesta:**
```json
{
  "success": true,
  "materias": [
    {"id": 1, "nombre": "Matemáticas"},
    {"id": 2, "nombre": "Literatura"}
  ]
}
```

#### **POST `/api/mensaje/enviar`**
Envía mensaje inicial a profesor.

**Body:**
```json
{
  "id_profesor": 3,
  "id_materia": 2,
  "titulo": "Consulta sobre...",
  "contenido": "Tengo una pregunta..."
}
```

---

### 5. 🎨 Vista (`Views/estudiante/mis_notificaciones.html`) - RENOVADA

#### **Características Principales:**

✅ **Modal Expandido**
- Ver mensaje completo del profesor
- Mostrar conversación completa (historial)
- Diseño profesional con gradientes

✅ **Sistema de Respuestas**
- Selector dinámico de materias
- Área de texto para respuesta
- Validación de campos

✅ **Conversación Visual**
- Mensajes del profesor en azul
- Mensajes del estudiante en verde
- Timestamps para cada mensaje
- Nombre del remitente identificable

✅ **Filtros Mejorados**
- "Todas" - Muestra todas las notificaciones
- "No leídas" - Solo las no leídas

✅ **Indicadores Visuales**
- Badge "NUEVO" para notificaciones sin leer
- Ícono de sobre abierto/cerrado
- Estilos diferenciados por estado

#### **Flujo de Usuario:**

```
1. Ver notificación en lista
   ↓
2. Click en notificación
   ↓
3. Modal abre con:
   - Mensaje completo del profesor
   - Historial de conversación
   - Formulario de respuesta
   ↓
4. Selecciona materia
   ↓
5. Escribe respuesta
   ↓
6. Click "Enviar Respuesta"
   ↓
7. Respuesta aparece en conversación
   ↓
8. Profesor recibe notificación
```

---

## 📱 Interfaz Usuario

### **Pantalla Principal - Notificaciones**

```
┌─────────────────────────────────────────┐
│ 📧 Notificaciones y Mensajes           │
├─────────────────────────────────────────┤
│                                         │
│ ✉️ [Todas (5)] [No leídas]             │
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📬 Retroalimentación de tarea [NUEVO]
│ │    Tu tarea necesita análisis...    ││
│ │    👨‍🏫 Dr. García | 🕐 14/11/2025   ││
│ │                              [↩️][🗑]  ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 📭 Calificaciones publicadas        ││
│ │    Las notas están disponibles...   ││
│ │    👨‍🏫 Dra. López | 🕐 13/11/2025    ││
│ │                              [↩️][🗑]  ││
│ └─────────────────────────────────────┘│
│                                         │
└─────────────────────────────────────────┘
```

### **Modal - Detalle y Respuesta**

```
┌───────────────────────────────────────────────┐
│ 📬 Retroalimentación de tarea            [×] │
├───────────────────────────────────────────────┤
│                                               │
│ Retroalimentación de tarea                   │
│ Tu tarea necesita más análisis de conceptos. │
│ 👨‍🏫 Dr. García | 🕐 14/11/2025 10:30:00     │
│                                               │
│ 💬 Conversación                              │
│ ┌─────────────────────────────────────────┐│
│ │ Dr. García                              ││
│ │ Tu tarea necesita análisis...          ││
│ │ 🕐 14/11/2025 10:30:00                 ││
│ └─────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────┐│
│ │ Tú                                      ││
│ │ Gracias, lo revisaré...                ││
│ │ 🕐 14/11/2025 11:00:00                 ││
│ └─────────────────────────────────────────┘│
│                                               │
├───────────────────────────────────────────────┤
│ Materia: [Matemáticas ▼]                     │
│ Tu respuesta:                                 │
│ ┌───────────────────────────────────────────┐│
│ │ Tengo una pregunta sobre el tema...       ││
│ └───────────────────────────────────────────┘│
│                    [Cancelar]  [📤 Enviar]   │
└───────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos

```
Estudiante                Base de Datos              Profesor
   │                          │                        │
   │─ Click en notificación ──│                        │
   │                          │                        │
   │◄─ Obtiene mensajes ──────│                        │
   │                          │◄─ Notificación enviada─┤
   │                          │                        │
   │─ Escribe respuesta ──────│                        │
   │                          │                        │
   │─ Envía respuesta ────────► Inserta en mensajes   │
   │                          │                        │
   │                          │─ Notifica profesor ───►│
   │                          │                        │
   │◄─ Recarga conversación ──│                        │
   │                          │                        │
```

---

## 🛠️ Configuración Requerida

### **1. Ejecutar Migración BD**
```bash
mysql GestionDeEstudiantes < Database/GestionEstduiante.sql
```

### **2. Verificar Modelo (Models/notificacion.py)**
Debe tener campo `id_profesor` con FOREIGN KEY.

### **3. Verificar Controlador**
`Controllers/notificacion_controller.py` debe tener método `obtener_notificaciones_estudiante()`.

### **4. Verificar Estudiante Controller**
`Controllers/estudiante_controller.py` debe tener método `obtener_materias_asignadas()`.

---

## 📊 Flujo Técnico Completo

### **1. Cargar Notificaciones**
```python
# main.py - Ruta /estudiante/notificaciones
notificaciones = NotificacionController.obtener_notificaciones_estudiante(id_estudiante)
# Retorna: [notif1, notif2, ...]
```

### **2. Abrir Modal**
```javascript
// mis_notificaciones.html - JS
fetch(`/api/notificacion/${id}`)
  // Obtiene: {notificacion, mensajes}
  // Renderiza detalles en modal
```

### **3. Cargar Materias**
```javascript
// mis_notificaciones.html - JS
fetch('/api/estudiante/materias')
  // Obtiene: [materia1, materia2, ...]
  // Rellena dropdown
```

### **4. Enviar Respuesta**
```javascript
// mis_notificaciones.html - JS
fetch(`/api/notificacion/${id}/responder`, {
  method: 'POST',
  body: {contenido, id_profesor, id_materia}
})
// Inserta en tabla mensajes
// Retorna: {success, mensaje_id}
```

---

## ✅ Checklist de Verificación

- [x] Tabla `mensajes` creada en BD
- [x] Modelo `Mensaje` implementado
- [x] Controlador `MensajeController` implementado
- [x] 4 APIs REST implementadas
- [x] Vista renovada con modal
- [x] Funcionalidad de respuesta completa
- [x] Selección de materia dinámica
- [x] Historial de conversación visible
- [x] Filtros de notificaciones funcionando
- [x] Indicadores visuales activos

---

## 📝 Notas Importantes

1. **Sincronización de Lectura:**
   - Al abrir el modal, automáticamente marca la notificación como leída
   - Los mensajes del profesor sin responder mostrarán estado "no leído"

2. **Materias:**
   - El selector de materias se carga dinámicamente del API
   - Solo muestra materias en las que el estudiante está inscrito

3. **Timestamps:**
   - Todos los mensajes tienen fecha/hora automática
   - Se almacenan en formato TIMESTAMP de MySQL

4. **Seguridad:**
   - Solo estudiantes autenticados pueden enviar respuestas
   - ID de profesor viene del sistema (no del cliente)
   - Validación en servidor de permisos

5. **Conversaciones:**
   - Se agrupa por notificación original
   - Historial completo siempre visible
   - Formato thread (estilo chat)

---

## 🚀 Próximas Mejoras Opcionales

- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Envío de emails cuando hay nuevas respuestas
- [ ] Adjuntos en mensajes
- [ ] Búsqueda en conversaciones
- [ ] Archivado de conversaciones
- [ ] Respuestas automáticas
- [ ] Calificación de respuestas del profesor

---

**Estado:** ✅ COMPLETADO Y LISTO PARA PRODUCCIÓN
