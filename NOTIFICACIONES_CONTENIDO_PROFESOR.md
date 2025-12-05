## 🔔 Funcionalidad de Notificaciones de Actualización de Contenido

### Descripción General

Se ha implementado un sistema completo que notifica a los profesores cuando no han actualizado el contenido de una materia en más de 3 días. El sistema incluye:

- **Tabla de seguimiento**: `profesor_actualizaciones_contenido` que registra la última actualización de contenido por profesor-materia.
- **Triggers automáticos**: Se actualizan automáticamente cuando el profesor sube o edita contenido.
- **Verificación de notificaciones**: Función que genera notificaciones al profesor cuando pasan 3+ días sin actualización.
- **Dashboard visual**: El profesor ve alertas de contenido desactualizado con códigos de color (rojo = urgente, amarillo = alerta, verde = actualizado).
- **Integración con BD existente**: La tabla `notificaciones` se usa para guardar los mensajes al profesor.

---

## 📋 Pasos de Instalación

### 1. Ejecutar el SQL de creación de tabla y triggers

Copia y ejecuta el contenido del archivo `Database/actualizacion_contenido_profesor.sql` en tu cliente MySQL:

```sql
-- Este archivo crea:
-- - Tabla profesor_actualizaciones_contenido
-- - Triggers para actualizar automáticamente
-- - Procedimiento para generar notificaciones
-- - Función para calcular días sin actualizar
```

**Ubicación del archivo:**
```
Database/actualizacion_contenido_profesor.sql
```

### 2. Cambios en `main.py`

Se agregaron dos funciones principales:

#### `verificar_y_generar_notificaciones_contenido(id_profesor=None)`
- Verifica si alguna materia del profesor no ha sido actualizada en 3+ días.
- Genera notificaciones automáticas en la tabla `notificaciones`.
- Se ejecuta automáticamente en el dashboard del profesor.

**Uso:**
```python
resultado = verificar_y_generar_notificaciones_contenido(id_profesor=123)
# Resultado:
# {
#     'status': 'ok',
#     'notificaciones_creadas': 2,
#     'materias_alerta': [
#         {'materia': 'Matemáticas', 'dias': 5},
#         {'materia': 'Inglés', 'dias': 4}
#     ]
# }
```

#### `obtener_materias_con_estado_contenido(id_profesor)`
- Obtiene todas las materias del profesor con el estado de actualización.
- Retorna información como días sin actualizar y estado (URGENTE, ALERTA, ACTUALIZADO).

**Uso:**
```python
materias = obtener_materias_con_estado_contenido(id_profesor=123)
# Retorna: [
#     {
#         'id': 1,
#         'nombre': 'Matemáticas',
#         'dias_sin_actualizar': 5,
#         'estado_contenido': 'URGENTE',
#         'color': '#f72585'
#     },
#     ...
# ]
```

### 3. Cambios en `Views/profesor/dashboard.html`

Se agregó una sección visual que muestra:

- **Banner de alerta** (si hay materias sin actualizar): Notifica al profesor y proporciona un enlace directo a "Contenidos".
- **Tarjetas por materia**: Muestra el estado de cada materia:
  - 🔴 **URGENTE**: Hace 3+ días sin actualización
  - 🟡 **ALERTA**: Hace 2-3 días sin actualización
  - 🟢 **ACTUALIZADO**: Hace menos de 2 días

---

## 🔧 Estructura de la Base de Datos

### Tabla: `profesor_actualizaciones_contenido`

```sql
CREATE TABLE profesor_actualizaciones_contenido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    ultima_actualizacion TIMESTAMP,
    notificacion_enviada BOOLEAN DEFAULT FALSE,
    fecha_notificacion TIMESTAMP NULL,
    UNIQUE KEY unique_profesor_materia (id_profesor, id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id),
    FOREIGN KEY (id_materia) REFERENCES materias(id)
);
```

**Campos principales:**
- `id_profesor`: Identificador del profesor
- `id_materia`: Identificador de la materia
- `ultima_actualizacion`: Timestamp de la última actualización de contenido
- `notificacion_enviada`: Indica si ya se envió la notificación
- `fecha_notificacion`: Cuándo se envió la notificación

### Triggers Automáticos

Se ejecutan cuando se inserta o actualiza contenido en `contenidos_materia`:

```sql
-- Trigger: actualizar_contenido_profesor_insert
-- Se ejecuta cuando se INSERTA contenido
-- Actualiza automáticamente la tabla profesor_actualizaciones_contenido

-- Trigger: actualizar_contenido_profesor_update
-- Se ejecuta cuando se ACTUALIZA contenido
-- Reinicia el contador de días
```

---

## 📊 Flujo de Trabajo

### Escenario 1: Profesor sube contenido

1. Profesor sube archivo en "Contenidos" → `contenidos_materia`
2. Trigger `actualizar_contenido_profesor_insert` se ejecuta automáticamente
3. `profesor_actualizaciones_contenido` se actualiza con `CURRENT_TIMESTAMP`
4. Campo `notificacion_enviada` se establece en `FALSE` (reset)

### Escenario 2: Dashboard del profesor

1. Profesor accede al dashboard
2. `profesor_dashboard()` en `main.py` se ejecuta
3. Llama a `verificar_y_generar_notificaciones_contenido(id_profesor)`
4. La función verifica cada materia:
   - Si hace 3+ días sin actualizar Y `notificacion_enviada = FALSE`
   - Crea notificación en tabla `notificaciones`
   - Marca como `notificacion_enviada = TRUE`
5. Template moestra alertas visuales

### Escenario 3: Profesor actualiza contenido después de alerta

1. Profesor sube nuevo contenido
2. Trigger actualiza `ultima_actualizacion` y `notificacion_enviada = FALSE`
3. Próxima vez que entre al dashboard, la alerta desaparece (porque ya no hace 3 días)

---

## 🎨 Estados Visuales en el Dashboard

| Estado | Color | Significado | Días sin actualizar |
|--------|-------|-------------|---------------------|
| URGENTE | 🔴 Rojo (#f72585) | Requiere actualización inmediata | >= 3 días |
| ALERTA | 🟡 Amarillo (#ffc107) | Próximamente vencerá | 2 días |
| ACTUALIZADO | 🟢 Verde (#28a745) | Contenido reciente | < 2 días |

---

## 📌 Notas Importantes

### Sobre los triggers

- Los triggers se ejecutan **automáticamente** cada vez que se inserta o edita contenido.
- No requieren intervención manual.
- Si necesitas desactivarlos temporalmente:
  ```sql
  SET SESSION sql_mode='';
  -- Ejecutar operaciones
  ```

### Sobre las notificaciones

- Las notificaciones se guardan en la tabla `notificaciones` existente.
- El campo `id_estudiante` se deja como `NULL` para notificaciones del sistema al profesor.
- Las notificaciones se crean UNA sola vez (cuando pasan los 3 días).
- Si el profesor actualiza contenido, el contador se reinicia.

### Sobre la BD

- Asegúrate de que tu BD esté actualizada con el DDL de `actualizacion_contenido_profesor.sql`.
- Si tienes contenidos previos que no estén registrados, puedes ejecutar:
  ```sql
  INSERT INTO profesor_actualizaciones_contenido (id_profesor, id_materia, ultima_actualizacion)
  SELECT DISTINCT id_profesor, id_materia, MAX(fecha_subida)
  FROM contenidos_materia
  GROUP BY id_profesor, id_materia
  ON DUPLICATE KEY UPDATE ultima_actualizacion = VALUES(ultima_actualizacion);
  ```

---

## 🧪 Pruebas Manuales

### Test 1: Verificar tabla creada

```sql
DESCRIBE profesor_actualizaciones_contenido;
SHOW TRIGGERS LIKE 'actualizar_contenido%';
```

### Test 2: Simular 3 días sin actualizar

```sql
-- Crear registro con fecha antigua
INSERT INTO profesor_actualizaciones_contenido (id_profesor, id_materia, ultima_actualizacion)
VALUES (1, 1, DATE_SUB(NOW(), INTERVAL 4 DAY))
ON DUPLICATE KEY UPDATE ultima_actualizacion = DATE_SUB(NOW(), INTERVAL 4 DAY);
```

Luego accede al dashboard del profesor → deberías ver una alerta roja.

### Test 3: Actualizar contenido

1. Profesor sube contenido en "Contenidos".
2. Verifica que `profesor_actualizaciones_contenido` se actualizó.
3. Accede al dashboard → la alerta debe desaparecer.

---

## 🚀 Próximas mejoras (Opcional)

- [ ] Enviar email al profesor cuando pasa el umbral de 3 días
- [ ] Historial de actualizaciones por materia
- [ ] Estadísticas de consistencia de contenidos
- [ ] Recordatorios automáticos por email

---

## 📞 Soporte

Si encuentras problemas:

1. Verifica que el SQL fue ejecutado correctamente
2. Revisa que `profesor_actualizaciones_contenido` existe: `SHOW TABLES LIKE '%actualiz%'`
3. Revisa los triggers: `SHOW TRIGGERS FROM GestionDeEstudiantes`
4. Consulta logs de error en la aplicación Flask

