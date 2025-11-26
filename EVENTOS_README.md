# Sistema de Eventos del Calendario - Guía de Implementación

## Descripción
Se ha agregado un sistema completo que permite a los estudiantes crear, editar y eliminar eventos personalizados en su calendario además de ver su horario de clases.

## Archivos Creados/Modificados

### Nuevos Archivos:
1. **Models/evento.py** - Modelo de datos para eventos
2. **Controllers/evento_controller.py** - Lógica de negocio para eventos
3. **Database/crear_tabla_eventos.sql** - Script SQL para crear la tabla

### Archivos Modificados:
1. **main.py** - Agregadas 7 rutas de API para CRUD de eventos
2. **Views/estudiante/mi_horario.html** - Interfaz mejorada con modal para crear eventos
3. **Database/GestionEstduiante.sql** - Tabla de eventos agregada

## Instalación de la Base de Datos

### Opción 1: Ejecutar el script SQL completo
```sql
-- Abrir tu cliente MySQL (phpMyAdmin, MySQL Workbench, etc.)
-- Ejecutar el archivo: Database/GestionEstduiante.sql
-- La tabla de eventos se creará automáticamente
```

### Opción 2: Crear solo la tabla de eventos
Si ya tienes tu base de datos actualizada, ejecuta:
```sql
USE GestionDeEstudiantes;

CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    color VARCHAR(7) DEFAULT '#4facfe',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    INDEX idx_estudiante (id_estudiante),
    INDEX idx_fecha (fecha),
    INDEX idx_estudiante_fecha (id_estudiante, fecha)
);
```

## Características del Sistema

### 1. Vista del Horario
- **Vista Semanal**: Muestra el horario de clases en una grilla de 5 días
- **Vista por Día**: Lista de clases organizadas por día de la semana

### 2. Crear Eventos
- Botón "Crear Evento" en la interfaz principal
- Modal intuitivo con campos:
  - Título del evento (requerido)
  - Descripción (opcional)
  - Fecha (requerido)
  - Hora de inicio y fin (requerido)
  - Selector de color (6 colores disponibles)

### 3. Funcionalidades
- ✅ Crear eventos personalizados
- ✅ Editar eventos existentes
- ✅ Eliminar eventos
- ✅ Validación de horas (inicio < fin)
- ✅ Selector de colores para diferencicar eventos
- ✅ Vista en tiempo real sin recargar página

## Rutas de API

### Crear Evento
```
POST /api/eventos/crear
Body: {
  "titulo": "Entregar proyecto",
  "descripcion": "Proyecto final de matemáticas",
  "fecha": "2025-11-20",
  "hora_inicio": "14:00",
  "hora_fin": "15:30",
  "color": "#4facfe"
}
```

### Obtener Todos los Eventos
```
GET /api/eventos/obtener
Response: {
  "success": true,
  "eventos": [...]
}
```

### Obtener Evento Específico
```
GET /api/eventos/obtener/<evento_id>
```

### Actualizar Evento
```
PUT /api/eventos/actualizar/<evento_id>
Body: {...datos del evento...}
```

### Eliminar Evento
```
DELETE /api/eventos/eliminar/<evento_id>
```

### Obtener Eventos por Fecha
```
GET /api/eventos/fecha/<fecha>
Ejemplo: /api/eventos/fecha/2025-11-20
```

### Obtener Eventos del Mes
```
GET /api/eventos/mes/<año>/<mes>
Ejemplo: /api/eventos/mes/2025/11
```

## Uso del Sistema

### Para Crear un Evento:
1. Acceder a la página "Mi Horario" como estudiante
2. Hacer clic en el botón "+ Crear Evento"
3. Completar el formulario:
   - Título (obligatorio)
   - Descripción (opcional)
   - Fecha (obligatorio)
   - Hora de inicio y fin (obligatorio)
   - Seleccionar color (opcional)
4. Hacer clic en "Guardar Evento"

### Para Editar un Evento:
1. En la vista por día, hacer clic en "Editar" en el evento deseado
2. Modificar los datos en el modal
3. Hacer clic en "Guardar Evento"

### Para Eliminar un Evento:
1. En la vista por día, hacer clic en "Eliminar" en el evento
2. Confirmar la eliminación

## Colores Disponibles

| Color | Código HEX |
|-------|-----------|
| Azul | #4facfe |
| Rojo | #ff6b6b |
| Verde | #51cf66 |
| Naranja | #ffa94d |
| Morado | #9775fa |
| Turquesa | #20c997 |

## Validaciones

- ✅ El título del evento es obligatorio
- ✅ La fecha y horas son obligatorias
- ✅ La hora de inicio debe ser menor a la hora de fin
- ✅ No se permite crear eventos en fechas pasadas
- ✅ Solo el estudiante propietario puede editar/eliminar sus eventos

## Estructura de Datos

### Tabla: eventos
```sql
- id (INT, PK, AUTO_INCREMENT)
- id_estudiante (INT, FK)
- titulo (VARCHAR 255)
- descripcion (TEXT)
- fecha (DATE)
- hora_inicio (TIME)
- hora_fin (TIME)
- color (VARCHAR 7, default #4facfe)
- creado_en (TIMESTAMP)
- actualizado_en (TIMESTAMP)
```

## Notas Técnicas

1. **Frontend**: HTML5, CSS3, JavaScript vanilla (sin dependencias externas)
2. **Backend**: Flask con Python
3. **Base de Datos**: MySQL con InnoDB
4. **Seguridad**: Solo estudiantes autenticados pueden crear eventos
5. **Aislamiento**: Los estudiantes solo pueden ver/editar sus propios eventos

## Troubleshooting

### Los eventos no aparecen:
1. Verifica que la tabla de eventos exista en la BD
2. Revisa que hayas ejecutado SQL correctamente
3. Abre la consola del navegador (F12) y busca errores en la red

### Error 401 (No autorizado):
1. Asegúrate de estar logeado como estudiante
2. Verifica que la sesión sea válida

### Error 500 en crear evento:
1. Revisa los logs del servidor Flask
2. Verifica la conexión a la base de datos
3. Confirma que los parámetros del formulario sean correctos

## Próximas Mejoras Sugeridas

1. Agregar repetición de eventos (cada semana, cada mes, etc.)
2. Compartir eventos con compañeros
3. Integración con Google Calendar
4. Notificaciones de recordatorio
5. Exportar calendario a PDF
6. Vista mensual tipo calendario tradicional
