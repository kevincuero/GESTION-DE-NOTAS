# 🚀 GUÍA RÁPIDA DE ACTIVACIÓN

## Solo 2 pasos para activar la funcionalidad

### PASO 1️⃣: Ejecutar SQL en tu BD

**Archivo:** `Database/actualizacion_contenido_profesor.sql`

```bash
# Opción A: MySQL CLI
mysql -u usuario -p GestionDeEstudiantes < Database/actualizacion_contenido_profesor.sql

# Opción B: Workbench/phpMyAdmin
# 1. Abre la herramienta
# 2. Copia todo el contenido de actualizacion_contenido_profesor.sql
# 3. Pega en la consola SQL
# 4. Ejecuta
```

**¿Qué hace?**
- Crea tabla `profesor_actualizaciones_contenido`
- Crea triggers automáticos que actualizan cuando subes contenido
- Crea función auxiliar para calcular días

### PASO 2️⃣: Reiniciar la aplicación

```bash
# En tu terminal, en la carpeta del proyecto
python main.py
```

---

## ✅ Verificación Rápida

### En MySQL (verifica que se creó todo)

```sql
-- Ver tabla creada
DESCRIBE profesor_actualizaciones_contenido;

-- Ver triggers
SHOW TRIGGERS LIKE 'actualizar_contenido%';

-- Debe mostrar 2 triggers (insert y update)
```

### En la aplicación

1. **Inicia sesión** como profesor
2. **Ve a dashboard** (opción del menú lateral)
3. Si alguna materia no tiene contenido en 3+ días → verás **alerta roja** 🔴

---

## 📦 Archivos Entregados

| Archivo | Descripción |
|---------|-------------|
| `Database/actualizacion_contenido_profesor.sql` | ⭐ EJECUTAR PRIMERO - DDL con triggers |
| `main.py` | ✏️ Modificado - Añadidas funciones helper |
| `Views/profesor/dashboard.html` | ✏️ Modificado - Alertas visuales |
| `NOTIFICACIONES_CONTENIDO_PROFESOR.md` | 📖 Documentación técnica completa |
| `RESUMEN_NOTIFICACIONES_CONTENIDO.md` | 📊 Documentación con ejemplos |

---

## 🎯 Qué hace la funcionalidad

### Para el profesor:
- ✅ Ve alertas en dashboard si debe actualizar contenido
- ✅ Alertas visuales claras: Rojo (urgente), Amarillo (próximo), Verde (OK)
- ✅ Enlace directo a "Contenidos" desde el banner de alerta
- ✅ Historial en tabla `notificaciones` de su cuenta

### Para el sistema:
- ✅ Rastrea automáticamente última actualización de contenido
- ✅ Genera notificaciones después de 3 días sin actualizar
- ✅ Las notificaciones se crean UNA sola vez (sin duplicados)
- ✅ Se reinicia cuando el profesor actualiza contenido

---

## ⚙️ Cambios Técnicos Realizados

### Nueva tabla SQL
```sql
CREATE TABLE profesor_actualizaciones_contenido (
    id_profesor INT,
    id_materia INT,
    ultima_actualizacion TIMESTAMP,
    notificacion_enviada BOOLEAN,
    fecha_notificacion TIMESTAMP
);
```

### Nuevas funciones Python (main.py)

```python
verificar_y_generar_notificaciones_contenido(id_profesor)
# → Verifica y crea notificaciones si hace 3+ días

obtener_materias_con_estado_contenido(id_profesor)
# → Obtiene estado actual de todas las materias
```

### Dashboard actualizado

- Banner rojo si hay alertas
- Tarjetas por materia con estado
- Colores intuitivos

---

## 🧪 Prueba Rápida

### Simular 3 días sin actualizar (para testing)

```sql
-- Crear registro con fecha antigua
INSERT INTO profesor_actualizaciones_contenido 
(id_profesor, id_materia, ultima_actualizacion)
VALUES (1, 1, DATE_SUB(NOW(), INTERVAL 4 DAY))
ON DUPLICATE KEY UPDATE 
    ultima_actualizacion = DATE_SUB(NOW(), INTERVAL 4 DAY);
```

Luego:
1. Accede al dashboard del profesor
2. Deberías ver alerta roja 🔴

---

## 📧 Próxima mejora (opcional)

Para enviar emails cuando se genere la notificación:
- Usar función `enviar_email_profesor()` existente
- Pasar asunto: "Contenido desactualizado en [Materia]"
- Pasar cuerpo: "Hace [X] días no actualizas contenido..."

---

## ❓ Preguntas Frecuentes

**P: ¿Qué pasa si el profesor sube contenido después de la alerta?**  
R: Se reinicia el contador, la alerta desaparece del dashboard.

**P: ¿Puedo cambiar los 3 días a otro número?**  
R: Sí, busca `>= 3` en SQL y Python, cámbialo por el número deseado.

**P: ¿Las notificaciones se guardan?**  
R: Sí, se guardan en tabla `notificaciones` con `id_estudiante = NULL`.

**P: ¿Funciona con múltiples profesores?**  
R: Sí, cada profesor tiene su propio seguimiento por materia.

---

## 🎊 ¡Listo!

Una vez hayas ejecutado el SQL y reiniciado la app, todo está operativo.

**Disfruta la nueva funcionalidad de notificaciones de actualización de contenido.** 🎉

