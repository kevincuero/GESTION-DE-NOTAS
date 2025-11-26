# 🚀 GUÍA DE IMPLEMENTACIÓN - SISTEMA DE RESPUESTAS

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos)
2. [Pasos de Implementación](#pasos)
3. [Verificación](#verificación)
4. [Troubleshooting](#troubleshooting)
5. [Uso del Sistema](#uso)

---

## 📋 Requisitos Previos {#requisitos}

### **Software Requerido:**
- ✅ Python 3.7+
- ✅ MySQL 5.7+ o MariaDB
- ✅ Flask 3.1.1
- ✅ mysql-connector-python 9.3.0

### **Acceso:**
- ✅ Acceso a terminal/PowerShell
- ✅ Acceso a MySQL (usuario admin)
- ✅ Acceso a archivos del proyecto

### **Base de Datos:**
- ✅ Base de datos `GestionDeEstudiantes` existente
- ✅ Tablas: estudiantes, profesores, notificaciones, materias

---

## 🔧 Pasos de Implementación {#pasos}

### **PASO 1: Actualizar Base de Datos**

#### Opción A: Usando MySQL CLI (recomendado)
```bash
# En PowerShell
cd c:\Users\USER\OneDrive\Escritorio\Universidad\semestre 6\Nueva carpeta\Campus\Campus

# Ejecutar script
mysql -u root -p GestionDeEstudiantes < Database/actualizar_bd_respuestas.sql
# Ingresar contraseña cuando se pida
```

#### Opción B: Usando MySQL Workbench
1. Abrir MySQL Workbench
2. Conectar a servidor local
3. Seleccionar base de datos `GestionDeEstudiantes`
4. File → Open SQL Script
5. Seleccionar `Database/actualizar_bd_respuestas.sql`
6. Ejecutar (Ctrl + Shift + Enter)

#### Opción C: Directo en MySQL Prompt
```sql
USE GestionDeEstudiantes;
-- Copiar y pegar contenido de Database/actualizar_bd_respuestas.sql
```

**Verificación:**
```sql
SELECT * FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'GestionDeEstudiantes' AND TABLE_NAME = 'mensajes';
# Debe devolver una fila
```

---

### **PASO 2: Verificar Archivos Creados**

```bash
# En PowerShell, verificar archivos existen:
Test-Path "Models/mensaje.py"                    # Debe ser True
Test-Path "Controllers/mensaje_controller.py"    # Debe ser True
Test-Path "Database/actualizar_bd_respuestas.sql" # Debe ser True
Test-Path "test_respuestas.py"                   # Debe ser True
```

**Salida esperada:**
```
True
True
True
True
```

---

### **PASO 3: Verificar Vista Renovada**

```bash
# Verificar que la vista fue actualizada
$contenido = Get-Content "Views/estudiante/mis_notificaciones.html"
if ($contenido -match "notificacionModal") { 
    Write-Host "✅ Vista actualizada correctamente"
} else {
    Write-Host "❌ Error: Vista no fue actualizada"
}
```

---

### **PASO 4: Reiniciar Flask**

```bash
# En PowerShell, en carpeta del proyecto
python main.py

# Salida esperada:
# WARNING in app.logger: 'authlib no está instalada...'
# WARNING in app.logger: 'Google OAuth deshabilitado...'
#  * Running on http://127.0.0.1:5000
```

**Si hay errores:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Luego reintentar
python main.py
```

---

### **PASO 5: Ejecutar Tests (Opcional)**

```bash
# En PowerShell
python test_respuestas.py

# Salida esperada:
# ==================================================
#   SUITE DE PRUEBAS - RESPUESTAS EN NOTIFICACIONES
# ==================================================
#
# 🧪 Test 1: Verificar tabla mensajes...
#    ✅ Tabla mensajes existe
#
# 🧪 Test 2: Crear mensaje...
#    ✅ Mensaje creado: ID 1
#
# ... (más tests)
#
# ==================================================
# RESUMEN
# ==================================================
# ✅ Pruebas pasadas: 7/7
# 🎉 TODAS LAS PRUEBAS PASARON
```

---

## ✅ Verificación {#verificación}

### **Checklist de Implementación:**

```
Tabla de BD:
  [ ] Tabla 'mensajes' existe
  [ ] 9 columnas creadas
  [ ] 4 índices activos
  [ ] Foreign keys funcionales

Código Python:
  [ ] Models/mensaje.py existe
  [ ] Controllers/mensaje_controller.py existe
  [ ] main.py tiene 4 nuevas rutas
  [ ] Imports correctos

Interfaz:
  [ ] mis_notificaciones.html renovada
  [ ] Modal funciona
  [ ] JavaScript incluido

Documentación:
  [ ] RESPUESTAS_NOTIFICACIONES.md existe
  [ ] RESUMEN_RESPUESTAS.md existe
  [ ] CAMBIOS_RESPUESTAS.md existe
  [ ] test_respuestas.py existe

Tests:
  [ ] test_respuestas.py ejecuta
  [ ] Todos los tests pasan
  [ ] BD conecta correctamente
```

### **Prueba Manual de APIs:**

Usar Postman o curl para probar:

```bash
# 1. Obtener notificación con conversación
curl -X GET http://localhost:5000/api/notificacion/1 \
  -H "Cookie: session=..."

# 2. Enviar respuesta
curl -X POST http://localhost:5000/api/notificacion/1/responder \
  -H "Content-Type: application/json" \
  -d '{"contenido":"Respuesta","id_profesor":1,"id_materia":1}'

# 3. Obtener materias
curl -X GET http://localhost:5000/api/estudiante/materias \
  -H "Cookie: session=..."

# 4. Enviar mensaje inicial
curl -X POST http://localhost:5000/api/mensaje/enviar \
  -H "Content-Type: application/json" \
  -d '{"id_profesor":1,"id_materia":1,"titulo":"Consulta","contenido":"..."}'
```

---

## 🐛 Troubleshooting {#troubleshooting}

### **Problema: "Tabla mensajes no existe"**

**Solución:**
```bash
# Verificar en MySQL
mysql -u root -p
USE GestionDeEstudiantes;
SHOW TABLES LIKE 'mensajes';

# Si no existe, ejecutar manualmente:
# (Ver contenido de Database/actualizar_bd_respuestas.sql)
```

---

### **Problema: "ModuleNotFoundError: No module named 'mensaje'"**

**Solución:**
```bash
# Verificar archivo existe
Test-Path "Models/mensaje.py"

# Si no existe, copiar desde LISTA_FINAL_ARCHIVOS.md
# Si existe, verificar imports en Controllers/mensaje_controller.py
```

---

### **Problema: "ModuleNotFoundError: No module named 'Controllers.mensaje_controller'"**

**Solución:**
```bash
# Verificar archivo existe
Test-Path "Controllers/mensaje_controller.py"

# Verificar import en main.py:
# from Controllers.mensaje_controller import MensajeController
```

---

### **Problema: Modal no abre al click en notificación**

**Solución:**
```javascript
// En consola del navegador (F12)
// Verificar que modal existe:
document.getElementById('notificacionModal')

// Verificar función existe:
typeof abrirModal

// Hacer click manual:
abrirModal(1, 1)
```

---

### **Problema: "Error al cargar materias"**

**Solución:**
```bash
# Verificar que estudiante tenga materias inscritas
mysql
SELECT * FROM inscripciones WHERE id_estudiante = 1;

# Si no hay resultados, inscribir estudiante a materia:
INSERT INTO inscripciones VALUES (1, 1);
```

---

### **Problema: "Error 500 al enviar respuesta"**

**Solución:**
```bash
# Ver logs de Flask
# Revisar que:
1. id_notificacion existe
2. id_estudiante es válido
3. id_profesor es válido
4. id_materia existe
5. contenido no está vacío
```

---

## 📱 Uso del Sistema {#uso}

### **Para Estudiante:**

#### **1. Ver Notificaciones**
```
1. Login como estudiante
2. Ir a "Mis Notificaciones" (sidebar)
3. Ver lista de notificaciones
```

#### **2. Abrir Notificación**
```
1. Click en la notificación o botón "Responder"
2. Modal se abre mostrando:
   - Mensaje completo del profesor
   - Historial de conversación
   - Formulario de respuesta
```

#### **3. Enviar Respuesta**
```
1. Seleccionar materia del dropdown
2. Escribir respuesta en textarea
3. Click "Enviar Respuesta"
4. Respuesta aparece en conversación
5. Modal se recarga automáticamente
```

#### **4. Filtrar Notificaciones**
```
- Click en "Todas" para ver todas
- Click en "No leídas" para ver solo no leídas
```

---

### **Para Profesor:**

#### **1. Enviar Notificación**
```
1. Login como profesor
2. Ir a "Enviar Notificación"
3. Elegir estudiante
4. Escribir mensaje
5. Enviar
```

#### **2. Ver Respuestas**
```
1. El profesor recibe notificación de respuesta
2. Puede ver respuesta en BD tabla mensajes
```

---

### **Flujo Completo de Conversación:**

```
Paso 1: Profesor envía notificación
   └─ Notificación guardada en tabla 'notificaciones'

Paso 2: Estudiante abre notificación
   └─ Carga mensajes de tabla 'mensajes'
   └─ Se marca notificación como leída

Paso 3: Estudiante responde
   └─ Respuesta se guarda en tabla 'mensajes'
   └─ remitente_tipo = 'estudiante'

Paso 4: Profesor ve respuesta
   └─ Profesor recibe notificación
   └─ Puede ver mensajes en conversación

Paso 5: Profesor responde
   └─ Nueva entrada en tabla 'mensajes'
   └─ remitente_tipo = 'profesor'

Paso 6: Conversación continúa...
   └─ Historial completo visible
   └─ Timestamps en cada mensaje
```

---

## 📊 Estructura de BD Final

```sql
-- Tabla notificaciones (existente)
notificaciones (
  id, id_estudiante, id_profesor, 
  titulo, mensaje, leida, fecha
)

-- Tabla mensajes (NUEVA)
mensajes (
  id,                    -- PK
  id_notificacion,       -- FK → notificaciones
  id_estudiante,         -- FK → estudiantes
  id_profesor,           -- FK → profesores
  id_materia,            -- FK → materias
  remitente_tipo,        -- 'estudiante' | 'profesor'
  contenido,             -- Texto del mensaje
  leido,                 -- Estado de lectura
  fecha                  -- Timestamp
)
```

---

## 🎯 Próximos Pasos

### **Después de Implementar:**

1. ✅ Probar con datos reales
2. ✅ Hacer backup de BD
3. ✅ Documentar procesos
4. ✅ Capacitar a usuarios
5. ✅ Monitorear logs

### **Mejoras Futuras:**

- [ ] Notificaciones en tiempo real
- [ ] Envío de emails
- [ ] Adjuntos de archivos
- [ ] Búsqueda en conversaciones
- [ ] Archivado de conversaciones

---

## 📞 Soporte

**En caso de problemas:**

1. Revisar `RESPUESTAS_NOTIFICACIONES.md` (referencia técnica)
2. Ejecutar `test_respuestas.py` (validación)
3. Revisar logs de Flask (errors)
4. Verificar BD (SQL queries)
5. Revisar Console del navegador (F12)

---

## ✅ Resumen de Checklist Final

```
Implementación Completada ✅

[ ] Base de datos actualizada
[ ] Archivos creados/modificados
[ ] Flask reiniciado
[ ] Tests ejecutados
[ ] Manual de usuario leído
[ ] Documentación revisada
[ ] Sistema probado
[ ] Equipo capacitado
[ ] Go-live autorizado

ESTADO: LISTO PARA PRODUCCIÓN ✅
```

---

**Última actualización:** 14 Noviembre 2025
**Versión de guía:** 1.0
**Soporte:** Ver RESPUESTAS_NOTIFICACIONES.md
