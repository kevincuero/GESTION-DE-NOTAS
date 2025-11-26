# Sistema de Índices de Aprendizaje

## Descripción
Sistema completo para que los docentes (profesores) evalúen índices de aprendizaje grupal de sus estudiantes. Permite crear, editar, evaluar y eliminar índices de aprendizaje por materia.

## Características

### 1. Crear Índices de Aprendizaje
- **Ubicación**: `/profesor/indices` → "Crear Nuevo Índice"
- **Campos**:
  - Nombre del índice (ej: "Resolución de Problemas")
  - Descripción (qué evalúa este índice)
  - Parcial/Evaluación asociada (Parcial 1, 2, 3 o Examen Final)
  - Porcentaje de importancia (0-100%)
- **Validaciones**:
  - Máximo 4 índices por materia
  - Suma total de porcentajes ≤ 100%
  - Nombre requerido

### 2. Evaluar Índices
- **Ubicación**: `/profesor/indices` → "Evaluar" (botón en tabla)
- **Acciones**:
  - Ver información actual del índice
  - Ver histórico de evaluaciones previas
  - Registrar nueva evaluación grupal
- **Campos de Evaluación**:
  - Porcentaje de dominio del grupo (0-100%)
  - Comentarios adicionales (opcional)
- **Información Mostrada**:
  - Última evaluación (fecha y porcentaje)
  - Promedio de dominio histórico

### 3. Editar Índices
- **Ubicación**: `/profesor/indices` → "Editar" (botón en tabla)
- **Campos Editables**: Nombre, descripción, parcial, porcentaje
- **Validaciones**: Aplican las mismas validaciones que al crear

### 4. Eliminar Índices
- **Ubicación**: `/profesor/indices` → "Eliminar" (botón en tabla)
- **Comportamiento**: Elimina el índice y todas sus evaluaciones asociadas

## Rutas Disponibles

### Backend (main.py)
```
GET  /profesor/indices              → Ver índices de una materia seleccionada
POST /profesor/indices              → Seleccionar materia para ver/crear índices
GET  /profesor/crear_indice         → Mostrar formulario de creación
POST /profesor/crear_indice         → Guardar nuevo índice
GET  /profesor/evaluar_indice/<id>  → Mostrar formulario de evaluación
POST /profesor/evaluar_indice/<id>  → Guardar evaluación
GET  /profesor/editar_indice/<id>   → Mostrar formulario de edición
POST /profesor/editar_indice/<id>   → Guardar cambios
GET  /profesor/eliminar_indice/<id> → Eliminar índice
```

## Estructura de Base de Datos

### Tabla: `indices_aprendizaje`
```sql
CREATE TABLE indices_aprendizaje (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_materia INT NOT NULL,
    id_profesor INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500),
    porcentaje DECIMAL(5, 2),
    parcial VARCHAR(50),
    fecha_creacion TIMESTAMP,
    FOREIGN KEY (id_materia) REFERENCES materias(id),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id)
);
```

### Tabla: `evaluaciones_indices`
```sql
CREATE TABLE evaluaciones_indices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_indice INT NOT NULL,
    id_profesor INT NOT NULL,
    porcentaje_dominio DECIMAL(5, 2),
    comentario TEXT,
    fecha_evaluacion TIMESTAMP,
    FOREIGN KEY (id_indice) REFERENCES indices_aprendizaje(id),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id)
);
```

## Instalación / Activación

### 1. Ejecutar Script SQL
Ejecuta el archivo `Database/indices_aprendizaje.sql` en tu base de datos MySQL:

```bash
mysql -u usuario -p GestionDeEstudiantes < Database/indices_aprendizaje.sql
```

O manualmente en tu cliente MySQL:
```sql
USE GestionDeEstudiantes;
-- Pegar contenido de Database/indices_aprendizaje.sql
```

### 2. Archivos Creados/Modificados

**Nuevos archivos:**
- `Models/indice_aprendizaje.py` - Modelo CRUD para índices
- `Models/evaluacion_indice.py` - Modelo CRUD para evaluaciones
- `Controllers/indices_controller.py` - Controlador de lógica de negocio
- `Views/profesor/indices.html` - Página principal de índices
- `Views/profesor/crear_indice.html` - Formulario crear/editar índices
- `Views/profesor/evaluar_indice.html` - Formulario de evaluación grupal
- `Database/indices_aprendizaje.sql` - Esquema de tablas

**Archivos modificados:**
- `main.py` - Se agregaron 6 nuevas rutas y se importó `IndicesController`
- `Views/profesor/dashboard.html` - Se conectó botón "Índices" a ruta real

### 3. Estructura de Carpetas
```
Campus/
├── Models/
│   ├── indice_aprendizaje.py        (NUEVO)
│   ├── evaluacion_indice.py         (NUEVO)
│   └── ...
├── Controllers/
│   ├── indices_controller.py        (NUEVO)
│   └── ...
├── Views/
│   └── profesor/
│       ├── indices.html             (NUEVO)
│       ├── crear_indice.html        (NUEVO)
│       ├── evaluar_indice.html      (NUEVO)
│       └── ...
├── Database/
│   ├── indices_aprendizaje.sql      (NUEVO)
│   └── ...
└── ...
```

## Flujo de Uso

### Para el Docente:

1. **Ir a Índices**: Dashboard → Sidebar "Índices"
2. **Seleccionar Materia**: Elegir una materia de la lista
3. **Ver Índices Existentes**: Se muestra tabla con índices de esa materia
4. **Crear Índice** (si < 4):
   - Clic en "Crear Nuevo Índice"
   - Llenar formulario
   - Guardar
5. **Evaluar Índice**:
   - Clic en "Evaluar" de un índice
   - Ver información e histórico
   - Registrar nuevo porcentaje de dominio
   - Agregar comentarios
   - Guardar
6. **Editar Índice**:
   - Clic en "Editar" de un índice
   - Modificar campos
   - Guardar cambios
7. **Eliminar Índice**:
   - Clic en "Eliminar" de un índice
   - Confirmar eliminación

## Validaciones Implementadas

✅ **Máximo 4 índices por materia**
```python
if total_indices >= 4:
    return {"success": False, "message": "No se pueden crear más de 4 índices..."}
```

✅ **Suma de porcentajes ≤ 100%**
```python
suma_porcentajes = sum(índices) + nuevo_porcentaje
if suma_porcentajes > 100:
    return {"success": False, "message": "La suma no puede exceder 100%..."}
```

✅ **Porcentaje de dominio 0-100%**
```python
if not (0 <= porcentaje_dominio <= 100):
    flash("El porcentaje debe estar entre 0 y 100.")
```

✅ **Autorización - Solo profesor propietario**
```python
if indice['id_profesor'] != id_profesor:
    flash("No tienes permisos.")
```

✅ **Campos requeridos** (validación HTML5 + backend)

## Consideraciones de Seguridad

- ✅ Validación de sesión: Solo usuarios con tipo 'profesor'
- ✅ Validación de propiedad: Solo puede editar/eliminar sus propios índices
- ✅ Validación de datos: Valores numéricos, ranges, longitudes
- ✅ Prevención de SQL injection: Queries parametrizadas
- ✅ CSRF token (Flask implicit): Sessions seguras

## Pruebas Recomendadas

### Pruebas de Creación
- [ ] Crear 4 índices en una materia (debe permitir)
- [ ] Intenta crear 5to índice (debe rechazar)
- [ ] Crear índices con suma de porcentajes > 100% (debe rechazar)
- [ ] Dejar campos requeridos vacíos (debe rechazar)

### Pruebas de Evaluación
- [ ] Evaluar un índice con 0% (debe permitir)
- [ ] Evaluar un índice con 100% (debe permitir)
- [ ] Evaluar con 101% (debe rechazar)
- [ ] Ver histórico de 3+ evaluaciones
- [ ] Verificar promedio de dominio se calcula correctamente

### Pruebas de Edición
- [ ] Editar nombre y guardar
- [ ] Editar porcentaje (verificar suma)
- [ ] Cambiar parcial asociado

### Pruebas de Eliminación
- [ ] Eliminar índice con evaluaciones (deben eliminarse en cascada)
- [ ] Verificar que se elimina de BD

### Pruebas de Seguridad
- [ ] Intentar acceder a índices de otra materia (sin permiso docente)
- [ ] Intentar evaluar índice de otro profesor (debe fallar)

## Mejoras Futuras (Opcional)

- 📌 Agregar reportes/gráficos de evolución de dominio
- 📌 Exportar evaluaciones a Excel/PDF
- 📌 Historial de cambios en índices (audit trail)
- 📌 Notificaciones a estudiantes sobre resultados
- 📌 Comparar dominio entre grupos de la misma materia
- 📌 Análisis estadístico de desempeño por índice

## Soporte / Debugging

**Error: "Selecciona una materia primero"**
- Cause: No se seleccionó materia
- Fix: Volver a `/profesor/indices` y seleccionar materia

**Error: "La suma de porcentajes no puede exceder 100%"**
- Cause: Total de porcentajes > 100%
- Fix: Reducir porcentaje de algunos índices

**Error: "No se pueden crear más de 4 índices"**
- Cause: Ya hay 4 índices en esa materia
- Fix: Editar o eliminar un índice existente primero

**Las evaluaciones no aparecen**
- Cause: No se creó la tabla en BD
- Fix: Ejecutar `Database/indices_aprendizaje.sql`

## Contacto
Si encuentras errores, verifica que:
1. Las tablas estén creadas en la BD
2. La conexión a BD esté funcionando
3. El usuario profesor tenga sesión iniciada
4. Los permisos de BD sean suficientes

---

**Última actualización**: $(date)
**Versión**: 1.0
**Estado**: ✅ Completo y funcional
