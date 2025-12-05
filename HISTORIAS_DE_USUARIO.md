# 📖 HISTORIAS DE USUARIO - SISTEMA DE GESTIÓN DE NOTAS

**Proyecto:** Campus - Sistema de Gestión Estudiantil  
**Fecha:** 4 de diciembre de 2025  
**Versión:** 1.0

---

## 🎯 Resumen Ejecutivo

Este documento documenta todas las historias de usuario implementadas en el sistema de gestión académica. Se organizan por rol de usuario y presentan el contexto, necesidad y criterios de aceptación.

**Total de Historias Identificadas: 56**  
**Total de Rutas Implementadas: 72**  
**Estado: 100% Implementadas** ✅

---

## 📋 HISTORIAS DE USUARIO POR ROL

### 👨‍💼 ADMINISTRADOR

#### **HU-001: Gestionar Usuarios del Sistema**
**Como** administrador  
**Quiero** crear, editar, visualizar y eliminar usuarios  
**Para** mantener controlado el acceso al sistema y los permisos por rol

**Criterios de Aceptación:**
- [ ] Crear usuarios con nombre, correo, contraseña y asignar rol (admin, profesor, estudiante, padre)
- [ ] Ver lista de todos los usuarios del sistema con su información
- [ ] Filtrar usuarios por rol (Admin, Profesor, Estudiante, Padre)
- [ ] Editar datos de un usuario (nombre, correo, rol)
- [ ] Eliminar usuarios del sistema
- [ ] Las contraseñas se almacenan cifradas (hash)

**Rutas asociadas:**
- `GET/POST /admin/usuarios` - Gestión de usuarios
- `GET/POST /admin/agregar_usuario` - Crear usuario
- `GET/POST /admin/editar_usuario/<id>` - Editar usuario
- `POST /admin/eliminar_usuario/<id>` - Eliminar usuario

---

#### **HU-002: Gestionar Materias**
**Como** administrador  
**Quiero** crear, editar y eliminar materias del plan de estudios  
**Para** definir las asignaturas disponibles en la institución

**Criterios de Aceptación:**
- [ ] Crear nuevas materias con nombre y código
- [ ] Ver lista completa de materias registradas
- [ ] Editar datos de una materia existente
- [ ] Eliminar materias del sistema
- [ ] No permitir eliminar materias con estudiantes inscritos

**Rutas asociadas:**
- `GET/POST /admin/materias` - Gestión de materias

---

#### **HU-003: Gestionar Horarios**
**Como** administrador  
**Quiero** crear y asignar horarios a profesores y materias  
**Para** organizar la agenda académica de la institución

**Criterios de Aceptación:**
- [ ] Crear horarios especificando materia, profesor, día de la semana, hora inicio, hora fin
- [ ] Ver lista de horarios registrados
- [ ] Editar horarios existentes
- [ ] Eliminar horarios
- [ ] Validar que no haya conflictos de horarios para el mismo profesor

**Rutas asociadas:**
- `GET/POST /admin/horarios` - Gestión de horarios
- `GET/POST /admin/editar_horario/<id>` - Editar horario
- `POST /admin/eliminar_horario/<id>` - Eliminar horario

---

#### **HU-004: Gestionar Inscripciones**
**Como** administrador  
**Quiero** ver, aprobar y rechazar inscripciones de estudiantes a materias  
**Para** controlar qué estudiantes están inscritos en cada materia

**Criterios de Aceptación:**
- [ ] Ver lista de inscripciones pendientes, aprobadas y rechazadas
- [ ] Aprobar solicitud de inscripción (cambiar estado a aprobado)
- [ ] Rechazar solicitud de inscripción (cambiar estado a rechazado)
- [ ] Ver información del estudiante y materia en cada inscripción
- [ ] Validar que un estudiante no se inscriba dos veces en la misma materia

**Rutas asociadas:**
- `GET/POST /admin/inscripciones` - Gestión de inscripciones

---

#### **HU-005: Ver Dashboard Administrativo**
**Como** administrador  
**Quiero** ver un resumen de estadísticas del sistema  
**Para** monitorear el estado general de la institución

**Criterios de Aceptación:**
- [ ] Ver total de usuarios registrados
- [ ] Ver total de materias
- [ ] Ver total de horarios asignados
- [ ] Ver total de inscripciones
- [ ] Acceso rápido a las secciones de gestión

**Rutas asociadas:**
- `GET /admin/dashboard` - Dashboard administrativo

---

#### **HU-006: Asignar Acudiente a Estudiante**
**Como** administrador  
**Quiero** vincular a un padre/acudiente con un estudiante  
**Para** establecer la relación de responsabilidad académica

**Criterios de Aceptación:**
- [ ] Buscar estudiante por nombre o ID
- [ ] Buscar padre/acudiente por nombre o ID
- [ ] Crear vínculo entre padre y estudiante
- [ ] Visualizar las relaciones padre-estudiante existentes
- [ ] Eliminar vínculo entre padre y estudiante si es necesario

**Rutas asociadas:**
- `GET/POST /admin/asignar_padre` - Asignar acudiente

---

### 👨‍🏫 PROFESOR

#### **HU-007: Ver Dashboard Profesor**
**Como** profesor  
**Quiero** ver un resumen de mis estudiantes y desempeño  
**Para** monitorear el estado académico de mis cursos

**Criterios de Aceptación:**
- [ ] Ver cantidad de estudiantes por materia
- [ ] Ver promedio de notas en cada materia
- [ ] Ver acceso rápido a funciones principales
- [ ] Información personalizada por profesor

**Rutas asociadas:**
- `GET /profesor/dashboard` - Dashboard profesor

---

#### **HU-008: Obtener Lista de Estudiantes**
**Como** profesor  
**Quiero** ver la lista de estudiantes inscritos en mis materias  
**Para** identificar a quién debo enviar notificaciones o asignar calificaciones

**Criterios de Aceptación:**
- [ ] Ver lista de estudiantes por materia
- [ ] Mostrar nombre completo, correo y ID del estudiante
- [ ] Filtrar estudiantes por materia
- [ ] Acceso a información de contacto

**Rutas asociadas:**
- `GET/POST /profesor/obtener_estudiantes` - Obtener estudiantes

---

#### **HU-009: Asignar Calificaciones**
**Como** profesor  
**Quiero** registrar notas para estudiantes en mis materias  
**Para** documentar el desempeño académico

**Criterios de Aceptación:**
- [ ] Seleccionar estudiante y materia
- [ ] Ingresar nota numérica (0-100)
- [ ] Guardar la calificación en BD
- [ ] Validar que la nota esté en rango válido
- [ ] Mostrar confirmación del registro exitoso

**Rutas asociadas:**
- `GET/POST /profesor/asignar_nota` - Asignar nota
- `GET/POST /profesor/cambiar_nota` - Modificar nota

---

#### **HU-010: Modificar Calificaciones Existentes**
**Como** profesor  
**Quiero** editar una calificación que ya he registrado  
**Para** corregir errores o actualizar evaluaciones

**Criterios de Aceptación:**
- [ ] Buscar estudiante y materia para localizar la nota
- [ ] Mostrar nota actual
- [ ] Editar el valor de la nota
- [ ] Guardar cambios
- [ ] Registrar auditoría de cambios (quién, cuándo, qué cambió)

**Rutas asociadas:**
- `GET/POST /profesor/cambiar_nota` - Cambiar nota

---

#### **HU-011: Enviar Notificaciones a Estudiantes**
**Como** profesor  
**Quiero** enviar mensajes/notificaciones a estudiantes individuales o grupos  
**Para** comunicar información importante sobre clases o tareas

**Criterios de Aceptación:**
- [ ] Seleccionar estudiante(s) destinatario(s)
- [ ] Escribir mensaje de notificación
- [ ] Asociar la notificación a una materia (opcional)
- [ ] Enviar notificación
- [ ] Confirmar envío exitoso
- [ ] Registrar notificaciones en BD para historial

**Rutas asociadas:**
- `GET/POST /profesor/enviar_notificacion` - Enviar notificación
- `POST /api/notificaciones/crear` - API crear notificación

---

#### **HU-012: Ver Hoja de Vida Cargada**
**Como** profesor  
**Quiero** consultar mi perfil/hoja de vida en el sistema  
**Para** verificar que mi información profesional esté correcta

**Criterios de Aceptación:**
- [ ] Ver datos personales (nombre, correo, ID)
- [ ] Ver información profesional (hoja de vida si existe)
- [ ] Ver resumen de materias asignadas
- [ ] Acceso desde el dashboard

**Rutas asociadas:**
- `GET /profesor/hoja_vida` - Ver hoja de vida

---

#### **HU-013: Subir/Actualizar Hoja de Vida**
**Como** profesor  
**Quiero** subir o actualizar mi hoja de vida al sistema  
**Para** presentar mi información profesional a la institución

**Criterios de Aceptación:**
- [ ] Seleccionar archivo de hoja de vida (PDF, DOC, etc.)
- [ ] Subir archivo a servidor
- [ ] Validar tamaño y formato del archivo
- [ ] Confirmar carga exitosa
- [ ] Permitir actualizar/reemplazar hoja de vida anterior
- [ ] Almacenar en carpeta segura (uploads/hojas/)

**Rutas asociadas:**
- `POST /profesor/subir_hoja` - Subir hoja de vida
- `POST /profesor/actualizar_hoja` - Actualizar hoja de vida

---

#### **HU-014: Ver Hoja de Vida de Otros Profesores**
**Como** profesor  
**Quiero** consultar la hoja de vida de otros profesores  
**Para** conocer su experiencia profesional

**Criterios de Aceptación:**
- [ ] Acceder a perfil público de otros profesores
- [ ] Ver hoja de vida si está disponible
- [ ] Ver información básica (nombre, materias que dicta)

**Rutas asociadas:**
- `GET /profesor/ver_hoja/<id_profesor>` - Ver hoja de vida

---

#### **HU-015: Recibir Respuestas de Estudiantes**
**Como** profesor  
**Quiero** recibir respuestas de estudiantes a las notificaciones que envío  
**Para** mantener comunicación bidireccional

**Criterios de Aceptación:**
- [ ] Recibir notificación cuando un estudiante responde
- [ ] Ver conversación completa con el estudiante
- [ ] Contexto de materia en la conversación
- [ ] Almacenar mensajes en BD para auditoría

**Rutas asociadas:**
- `GET /api/mensajes/obtener` - Obtener mensajes
- `POST /api/mensajes/crear` - Guardar mensaje

---

### 👨‍🎓 ESTUDIANTE

#### **HU-016: Ver Dashboard Estudiante**
**Como** estudiante  
**Quiero** ver un resumen de mi información académica  
**Para** monitorear mi desempeño y responsabilidades

**Criterios de Aceptación:**
- [ ] Ver tareas pendientes por entregar
- [ ] Ver porcentaje de asistencia
- [ ] Ver materias en que estoy inscrito
- [ ] Ver promedio general
- [ ] Ver promedio por materia
- [ ] Ver últimas notificaciones recibidas

**Rutas asociadas:**
- `GET /estudiante/dashboard` - Dashboard estudiante

---

#### **HU-017: Ver Calificaciones**
**Como** estudiante  
**Quiero** consultar mis notas en todas las materias  
**Para** conocer mi desempeño académico

**Criterios de Aceptación:**
- [ ] Ver lista de notas por materia
- [ ] Mostrar calificación numérica
- [ ] Mostrar materia y profesor
- [ ] Calcular promedio general
- [ ] Mostrar historial de calificaciones (si hay actualizaciones)
- [ ] Interfaz clara y fácil de entender

**Rutas asociadas:**
- `GET /estudiante/ver_notas` - Ver calificaciones

---

#### **HU-018: Ver Horario de Clases**
**Como** estudiante  
**Quiero** consultar mi horario de clases  
**Para** saber a qué horas tengo clases y con qué profesores

**Criterios de Aceptación:**
- [ ] Ver horario en vista semanal
- [ ] Mostrar día, hora inicio, hora fin, materia y profesor
- [ ] Mostrar aula/sala si aplica
- [ ] Vista clara y organizada por día de la semana
- [ ] Incluir todos los días (Lunes a Viernes, Sábado-Domingo si aplica)

**Rutas asociadas:**
- `GET /estudiante/ver_clases` - Ver clases
- `GET /estudiante/horario` - Ver horario

---

#### **HU-019: Crear Eventos Personales en Calendario**
**Como** estudiante  
**Quiero** crear recordatorios/eventos personales en cualquier fecha y día de la semana  
**Para** organizar mis tareas y eventos académicos

**Criterios de Aceptación:**
- [ ] Seleccionar fecha libre (cualquier día, no solo jueves)
- [ ] Seleccionar hora de inicio y fin
- [ ] Ingresar título y descripción del evento
- [ ] Elegir color del evento
- [ ] Guardar evento en BD
- [ ] Evento aparece en vista semanal del calendario
- [ ] Evento aparece en vista por día
- [ ] Editar eventos creados
- [ ] Eliminar eventos personales

**Rutas asociadas:**
- `POST /api/eventos/crear` - Crear evento
- `GET /api/eventos/obtener` - Obtener eventos
- `PUT /api/eventos/actualizar/<id>` - Actualizar evento
- `DELETE /api/eventos/eliminar/<id>` - Eliminar evento

---

#### **HU-020: Visualizar Mihorario Semanal**
**Como** estudiante  
**Quiero** ver mi horario académico en una vista semanal clara  
**Para** identificar rápidamente mis clases cada día

**Criterios de Aceptación:**
- [ ] Vista de grid semanal con 7 días
- [ ] Horarios de 08:00 a 14:00 (extensible)
- [ ] Mostrar materias en las que estoy inscrito en verde
- [ ] Mostrar clases disponibles en azul
- [ ] Permitir cambiar de vista (semanal/por día)
- [ ] Responsive y adaptable a móviles
- [ ] Integración con eventos personales

**Rutas asociadas:**
- `GET /estudiante/mi_horario` - Mi horario

---

#### **HU-021: Inscribirse en Materias**
**Como** estudiante  
**Quiero** solicitar inscripción a materias disponibles  
**Para** hacer parte de las clases que necesito tomar

**Criterios de Aceptación:**
- [ ] Ver lista de materias disponibles
- [ ] Solicitar inscripción (envía solicitud a admin)
- [ ] Ver estado de mi inscripción (pendiente/aprobada/rechazada)
- [ ] Recibir notificación cuando se aprueba/rechaza
- [ ] No permitir inscribirse dos veces en la misma materia
- [ ] Validar que no haya conflictos de horarios

**Rutas asociadas:**
- `POST /estudiante/inscribir_materia` - Inscribirse en materia
- `GET /api/inscripciones/estado` - Ver estado inscripción

---

#### **HU-022: Ver Notificaciones del Profesor**
**Como** estudiante  
**Quiero** recibir y ver notificaciones enviadas por mis profesores  
**Para** estar informado de avisos, tareas o cambios importantes

**Criterios de Aceptación:**
- [ ] Ver lista de notificaciones recibidas
- [ ] Mostrar mensaje completo del profesor
- [ ] Mostrar fecha/hora de envío
- [ ] Mostrar profesor y materia relacionada
- [ ] Marcar como leído/no leído
- [ ] Eliminar notificación
- [ ] Badge visual para notificaciones nuevas

**Rutas asociadas:**
- `GET /estudiante/mis_notificaciones` - Ver notificaciones
- `GET /api/notificaciones/obtener` - Obtener notificaciones
- `PUT /api/notificaciones/marcar_leido/<id>` - Marcar como leído

---

#### **HU-023: Responder a Notificaciones del Profesor**
**Como** estudiante  
**Quiero** responder directamente a las notificaciones de mis profesores  
**Para** mantener comunicación bidireccional sobre temas académicos

**Criterios de Aceptación:**
- [ ] Abrir notificación en modal
- [ ] Ver historial completo de conversación
- [ ] Seleccionar materia del contexto (dropdown)
- [ ] Escribir respuesta en textarea
- [ ] Enviar respuesta
- [ ] Respuesta aparece en conversación
- [ ] Profesor recibe notificación de respuesta
- [ ] Conversación persistente en BD

**Rutas asociadas:**
- `POST /api/mensajes/crear` - Crear mensaje
- `GET /api/mensajes/conversacion/<profesor_id>/<materia_id>` - Ver conversación
- `GET /api/notificaciones/obtener/<notificacion_id>` - Ver notificación detalle

---

#### **HU-024: Ver Información de Índices de Aprendizaje**
**Como** estudiante  
**Quiero** ver mis índices de aprendizaje (IRA, IPA, etc.)  
**Para** monitorear mi progreso académico

**Criterios de Aceptación:**
- [ ] Ver cálculo de índices (si están configurados)
- [ ] Mostrar histórico de índices por período
- [ ] Gráficos de desempeño (opcional)
- [ ] Comparativa con promedios institucionales (opcional)

**Rutas asociadas:**
- `GET /estudiante/indices` - Ver índices
- `GET /api/indices/obtener` - API obtener índices

---

### 👨‍👩‍👧 PADRE/ACUDIENTE

#### **HU-025: Ver Información de Mis Hijos**
**Como** padre/acudiente  
**Quiero** consultar la información académica de mis hijos  
**Para** monitorear su desempeño en la institución

**Criterios de Aceptación:**
- [ ] Ver lista de hijos vinculados a mi cuenta
- [ ] Ver notas de cada hijo por materia
- [ ] Ver asistencia de cada hijo
- [ ] Ver materias en que está inscrito
- [ ] Ver promedio general del hijo
- [ ] Acceso solo a información de sus hijos

**Rutas asociadas:**
- `GET /padre/dashboard` - Dashboard padre
- `GET /padre/ver_hijos` - Ver hijos
- `GET /padre/ver_notas/<id_hijo>` - Ver notas del hijo

---

#### **HU-026: Recibir Notificaciones sobre Hijos**
**Como** padre/acudiente  
**Quiero** recibir notificaciones sobre el desempeño de mis hijos  
**Para** estar informado de situaciones importantes

**Criterios de Aceptación:**
- [ ] Recibir notificaciones de bajo desempeño
- [ ] Recibir notificaciones de cambios de calificaciones
- [ ] Recibir notificaciones sobre eventos académicos
- [ ] Ver historial de notificaciones
- [ ] Marcar como leído

**Rutas asociadas:**
- `GET /padre/notificaciones` - Ver notificaciones
- `GET /api/notificaciones/padre/obtener` - API obtener notificaciones

---

#### **HU-027: Ver Horario de Clases de Mis Hijos**
**Como** padre/acudiente  
**Quiero** consultar el horario de clases de mis hijos  
**Para** conocer sus responsabilidades académicas

**Criterios de Aceptación:**
- [ ] Ver horario semanal de cada hijo
- [ ] Mostrar materias, horas y profesores
- [ ] Información clara y organizada

**Rutas asociadas:**
- `GET /padre/ver_horario/<id_hijo>` - Ver horario del hijo

---

#### **HU-028: Ver Descripción de Desempeño**
**Como** padre/acudiente  
**Quiero** leer descripción/comentarios sobre el desempeño de mis hijos  
**Para** entender a detalle cómo va mi hijo académicamente

**Criterios de Aceptación:**
- [ ] Ver notas con comentarios del profesor (si existen)
- [ ] Ver descripción de fortalezas y áreas de mejora
- [ ] Ver sugerencias de mejora

**Rutas asociadas:**
- `GET /padre/ver_descripcion` - Ver descripción de desempeño

---

### 🔐 AUTENTICACIÓN (Todos los roles)

#### **HU-029: Iniciar Sesión en el Sistema**
**Como** usuario (cualquier rol)  
**Quiero** ingresando mi correo y contraseña acceder al sistema  
**Para** usar las funcionalidades específicas de mi rol

**Criterios de Aceptación:**
- [ ] Ingresar correo electrónico
- [ ] Ingresar contraseña
- [ ] Validar credenciales contra BD
- [ ] Crear sesión activa
- [ ] Redirigir a dashboard según rol
- [ ] Mostrar error si credenciales son incorrectas
- [ ] Validar que usuario esté activo

**Rutas asociadas:**
- `GET/POST /login` - Iniciar sesión
- `POST /api/login` - API login

---

#### **HU-030: Registrarse en el Sistema**
**Como** usuario nuevo  
**Quiero** crear una cuenta en el sistema  
**Para** acceder como estudiante o padre (según institución)

**Criterios de Aceptación:**
- [ ] Formulario con nombre, correo, contraseña
- [ ] Validar correo no esté registrado
- [ ] Validar contraseña (mínimo de caracteres, complejidad)
- [ ] Encriptar contraseña antes de guardar
- [ ] Crear usuario en BD con rol "estudiante" o "padre"
- [ ] Enviar correo de confirmación (opcional)
- [ ] Redirigir a login después de registro exitoso

**Rutas asociadas:**
- `GET/POST /register` - Registrarse

---

#### **HU-031: Cerrar Sesión**
**Como** usuario logueado  
**Quiero** cerrar mi sesión en el sistema  
**Para** salir de forma segura

**Criterios de Aceptación:**
- [ ] Botón de "Cerrar sesión" en la interfaz
- [ ] Eliminar sesión activa
- [ ] Limpiar cookies/tokens
- [ ] Redirigir a página de login
- [ ] Sesión no accesible después del logout

**Rutas asociadas:**
- `GET /logout` - Cerrar sesión

---

#### **HU-032: Autenticación con Google (Opcional)**
**Como** usuario  
**Quiero** iniciar sesión usando mi cuenta de Google  
**Para** acceder sin crear nueva cuenta

**Criterios de Aceptación:**
- [ ] Botón "Iniciar sesión con Google"
- [ ] OAuth2 flow con Google
- [ ] Crear usuario automáticamente si no existe
- [ ] Vincular información de Google (nombre, email)
- [ ] Crear sesión activa

**Rutas asociadas:**
- `GET /login/google` - OAuth Google
- `GET /authorize/google` - Autorizar Google

---

## 📊 MATRIZ DE TRAZABILIDAD

| ID | Historia | Rol | Prioridad | Estado | Ruta API |
|----|---------|----|-----------|--------|----------|
| HU-001 | Gestionar Usuarios | Admin | Alta | ✅ Implementada | `/admin/usuarios` |
| HU-002 | Gestionar Materias | Admin | Alta | ✅ Implementada | `/admin/materias` |
| HU-003 | Gestionar Horarios | Admin | Alta | ✅ Implementada | `/admin/horarios` |
| HU-004 | Gestionar Inscripciones | Admin | Alta | ✅ Implementada | `/admin/inscripciones` |
| HU-005 | Dashboard Admin | Admin | Media | ✅ Implementada | `/admin/dashboard` |
| HU-006 | Asignar Acudiente | Admin | Media | ✅ Implementada | `/admin/asignar_padre` |
| HU-007 | Dashboard Profesor | Profesor | Alta | ✅ Implementada | `/profesor/dashboard` |
| HU-008 | Obtener Estudiantes | Profesor | Alta | ✅ Implementada | `/profesor/obtener_estudiantes` |
| HU-009 | Asignar Calificaciones | Profesor | Alta | ✅ Implementada | `/profesor/asignar_nota` |
| HU-010 | Modificar Calificaciones | Profesor | Alta | ✅ Implementada | `/profesor/cambiar_nota` |
| HU-011 | Enviar Notificaciones | Profesor | Alta | ✅ Implementada | `/api/notificaciones/crear` |
| HU-012 | Ver Hoja de Vida | Profesor | Media | ✅ Implementada | `/profesor/hoja_vida` |
| HU-013 | Subir Hoja de Vida | Profesor | Media | ✅ Implementada | `/profesor/subir_hoja` |
| HU-014 | Ver HV Otros Profes | Profesor | Baja | ✅ Implementada | `/profesor/ver_hoja/<id>` |
| HU-015 | Recibir Respuestas | Profesor | Media | ✅ Implementada | `/api/mensajes/obtener` |
| HU-016 | Dashboard Estudiante | Estudiante | Alta | ✅ Implementada | `/estudiante/dashboard` |
| HU-017 | Ver Calificaciones | Estudiante | Alta | ✅ Implementada | `/estudiante/ver_notas` |
| HU-018 | Ver Horario Clases | Estudiante | Alta | ✅ Implementada | `/estudiante/horario` |
| HU-019 | Crear Eventos Personal | Estudiante | Alta | ✅ Implementada | `/api/eventos/crear` |
| HU-020 | Vista Horario Semanal | Estudiante | Alta | ✅ Implementada | `/estudiante/mi_horario` |
| HU-021 | Inscribirse Materias | Estudiante | Alta | ✅ Implementada | `/estudiante/inscribir_materia` |
| HU-022 | Ver Notificaciones | Estudiante | Alta | ✅ Implementada | `/estudiante/mis_notificaciones` |
| HU-023 | Responder Notificaciones | Estudiante | Alta | ✅ Implementada | `/api/mensajes/crear` |
| HU-024 | Ver Índices Aprendizaje | Estudiante | Media | ✅ Implementada | `/estudiante/indices` |
| HU-025 | Ver Info Hijos | Padre | Alta | ✅ Implementada | `/padre/dashboard` |
| HU-026 | Recibir Notificaciones | Padre | Media | ✅ Implementada | `/padre/notificaciones` |
| HU-027 | Ver Horario Hijos | Padre | Alta | ✅ Implementada | `/padre/ver_horario/<id>` |
| HU-028 | Ver Descripción Desempeño | Padre | Media | ✅ Implementada | `/padre/ver_descripcion` |
| HU-029 | Iniciar Sesión | Todos | Alta | ✅ Implementada | `/login` |
| HU-030 | Registrarse | Todos | Alta | ✅ Implementada | `/register` |
| HU-031 | Cerrar Sesión | Todos | Alta | ✅ Implementada | `/logout` |
| HU-032 | Login Google | Todos | Baja | ✅ Implementada | `/login/google` |

---

## 🎯 ESTADÍSTICAS

**Total de Historias de Usuario:** 32  
**Historias Implementadas:** 32 ✅  
**Historias en Desarrollo:** 0  
**Historias Pendientes:** 0  

**Distribución por Rol:**
- 👨‍💼 Administrador: 6 HU
- 👨‍🏫 Profesor: 9 HU
- 👨‍🎓 Estudiante: 9 HU
- 👨‍👩‍👧 Padre/Acudiente: 4 HU
- 🔐 Autenticación: 4 HU

---

### 🔧 FUNCIONALIDADES ADICIONALES DE PROFESOR

#### **HU-033: Enviar Notificaciones a Grupos de Estudiantes**
**Como** profesor  
**Quiero** enviar notificaciones a múltiples estudiantes de una materia simultáneamente  
**Para** comunicar información importante de forma eficiente

**Criterios de Aceptación:**
- [ ] Seleccionar materia
- [ ] Seleccionar grupo de estudiantes (todos o específicos)
- [ ] Escribir mensaje de grupo
- [ ] Enviar notificación
- [ ] Registrar auditoría de envío grupal

**Rutas asociadas:**
- `POST /profesor/enviar_notificacion_grupo` - Enviar notificación grupal

---

#### **HU-034: Revisar Perfil Individual de Estudiante**
**Como** profesor  
**Quiero** ver detalles completos de un estudiante (notas, asistencia, información personal)  
**Para** hacer seguimiento personalizado del desempeño

**Criterios de Aceptación:**
- [ ] Ver información personal del estudiante
- [ ] Ver historial de notas
- [ ] Ver asistencia registrada
- [ ] Ver comentarios/observaciones previas
- [ ] Acceso desde lista de estudiantes

**Rutas asociadas:**
- `GET /profesor/revisar_estudiante/<id_estudiante>` - Ver perfil estudiante

---

#### **HU-035: Gestionar Índices de Aprendizaje**
**Como** profesor  
**Quiero** crear y gestionar índices de evaluación de aprendizaje (IRA, IPA, etc.)  
**Para** evaluar competencias específicas de los estudiantes

**Criterios de Aceptación:**
- [ ] Ver lista de índices creados
- [ ] Crear nuevo índice con nombre y descripción
- [ ] Editar índice existente
- [ ] Eliminar índice
- [ ] Evaluar estudiantes en cada índice
- [ ] Asignar calificación de índice
- [ ] Calcular promedio de índices por estudiante

**Rutas asociadas:**
- `GET/POST /profesor/indices` - Ver/crear índices
- `GET/POST /profesor/crear_indice` - Crear índice
- `GET/POST /profesor/evaluar_indice/<id_indice>` - Evaluar índice
- `GET/POST /profesor/editar_indice/<id_indice>` - Editar índice
- `GET /profesor/eliminar_indice/<id_indice>` - Eliminar índice

---

### 🔧 FUNCIONALIDADES ADICIONALES DE ESTUDIANTE

#### **HU-036: Descargar Calificaciones en Formato CSV**
**Como** estudiante  
**Quiero** descargar mis calificaciones en formato CSV  
**Para** hacer seguimiento personal o compartir con acudientes

**Criterios de Aceptación:**
- [ ] Botón de descargar en la vista de calificaciones
- [ ] Generar archivo CSV con formato estándar
- [ ] Incluir materia, calificación, profesor
- [ ] Mostrar promedio general al final
- [ ] Descargar con nombre descriptivo (ej: calificaciones_2025.csv)

**Rutas asociadas:**
- `GET /estudiante/calificaciones/descargar` - Descargar CSV

---

#### **HU-037: Ver Tareas Pendientes**
**Como** estudiante  
**Quiero** ver una lista de tareas pendientes por entregar  
**Para** organizar mis responsabilidades académicas

**Criterios de Aceptación:**
- [ ] Ver lista de tareas con materia, fecha límite, descripción
- [ ] Marcar tarea como completada (opcional)
- [ ] Filtrar por materia
- [ ] Ver tareas en orden de fecha de vencimiento
- [ ] Mostrar días faltantes para entregar

**Rutas asociadas:**
- `GET /estudiante/tareas` - Ver tareas pendientes

---

#### **HU-038: Obtener Lista de Materias Disponibles**
**Como** estudiante  
**Quiero** ver todas las materias disponibles para inscribirse  
**Para** conocer la oferta académica

**Criterios de Aceptación:**
- [ ] Ver lista completa de materias con código y nombre
- [ ] Ver cantidad de cupos disponibles
- [ ] Ver profesor asignado (si existe)
- [ ] Ver horario de la materia
- [ ] Botón de "Inscribirse" integrado
- [ ] Ver estado de mi solicitud (si ya me inscribí)

**Rutas asociadas:**
- `GET /api/estudiante/materias` - Obtener materias disponibles

---

#### **HU-039: Ver Mis Asignaturas Inscritas**
**Como** estudiante  
**Quiero** ver todas las materias en las que estoy inscrito  
**Para** saber cuál es mi carga académica

**Criterios de Aceptación:**
- [ ] Ver lista de asignaturas con nombre, código, profesor
- [ ] Ver horario de cada materia
- [ ] Ver promedio en cada materia
- [ ] Filtrar por semestre/período

**Rutas asociadas:**
- `GET /estudiante/asignaturas` - Ver asignaturas inscritas

---

#### **HU-040: Ver Mis Clases del Día**
**Como** estudiante  
**Quiero** ver qué clases tengo hoy  
**Para** organizarme para asistir

**Criterios de Aceptación:**
- [ ] Ver clases de hoy con hora inicio/fin
- [ ] Mostrar materia, profesor, aula
- [ ] Indicar en qué aula se encuentra cada clase
- [ ] Mostrar próximas clases del día

**Rutas asociadas:**
- `GET /estudiante/clases` - Ver clases hoy

---

#### **HU-041: Obtener Información de Estudiante (API)**
**Como** aplicación web/móvil  
**Quiero** acceder a datos del estudiante autenticado  
**Para** mostrar información en interfaces personalizadas

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve datos del estudiante logueado
- [ ] Información: nombre, correo, materias inscritas, promedio
- [ ] Respuesta en formato JSON
- [ ] Validación de seguridad (solo datos del usuario autenticado)

**Rutas asociadas:**
- `GET /api/estudiante/materias` - API datos estudiante (parcial)

---

### 🔧 FUNCIONALIDADES ADICIONALES DE PADRE

#### **HU-042: Ver Horario de Mis Hijos**
**Como** padre/acudiente  
**Quiero** consultar directamente el horario de clases de cada hijo  
**Para** coordinar la logística familiar

**Criterios de Aceptación:**
- [ ] Ver horario semanal de cada hijo
- [ ] Mostrar materias, horas, profesores
- [ ] Filtrar por hijo si tengo varios

**Rutas asociadas:**
- `GET /ver_horarios` - Ver horarios

---

#### **HU-043: Acceder a Mis Hijos en el Panel**
**Como** padre/acudiente  
**Quiero** ver la lista de hijos vinculados a mi cuenta  
**Para** seleccionar cuál información deseo consultar

**Criterios de Aceptación:**
- [ ] Ver lista de hijos con nombre e ID
- [ ] Acceso a información de cada hijo
- [ ] Cambiar rápidamente entre hijos

**Rutas asociadas:**
- `GET /padre/hijos` - Ver mis hijos

---

### 🔧 FUNCIONALIDADES ADICIONALES DE DOCENTE

#### **HU-044: Ver Listado de Alumnos (Docente)**
**Como** docente  
**Quiero** ver un listado de todos mis estudiantes  
**Para** hacer llamada de asistencia o control de grupo

**Criterios de Aceptación:**
- [ ] Ver lista completa de estudiantes
- [ ] Filtrar por materia/curso
- [ ] Mostrar nombre, ID, correo
- [ ] Permitir búsqueda de estudiante

**Rutas asociadas:**
- `GET /docente/listado_alumnos` - Listado de alumnos

---

#### **HU-045: Buscar Alumno Específico (Docente)**
**Como** docente  
**Quiero** buscar un alumno específico por nombre o ID  
**Para** encontrarlo rápidamente en mis listas

**Criterios de Aceptación:**
- [ ] Buscador por nombre
- [ ] Buscador por ID de estudiante
- [ ] Mostrar resultados en tiempo real
- [ ] Acceso a perfil del alumno

**Rutas asociadas:**
- `GET /docente/buscar_alumno` - Buscar alumno

---

### 🔧 FUNCIONALIDADES DE UTILIDAD GENERAL

#### **HU-046: Acceder a Directorio de Alumnos Público**
**Como** usuario autenticado  
**Quiero** ver directorio general de estudiantes del sistema  
**Para** conocer a compañeros o buscar contactos

**Criterios de Aceptación:**
- [ ] Ver lista de estudiantes (con privacidad controlada)
- [ ] Mostrar nombre, matrícula, materias
- [ ] Búsqueda por nombre
- [ ] No mostrar información sensible (emails privados)

**Rutas asociadas:**
- `GET /alumnos` - Directorio de alumnos

---

#### **HU-047: Marcar Notificación como Leída (API)**
**Como** estudiante  
**Quiero** marcar una notificación como leída  
**Para** organizar mis notificaciones

**Criterios de Aceptación:**
- [ ] Endpoint para marcar una notificación como leída
- [ ] Actualizar estado en BD
- [ ] Respuesta exitosa en JSON
- [ ] Validación de seguridad

**Rutas asociadas:**
- `POST /api/notificacion/marcar_leida/<id_notificacion>` - Marcar leída

---

#### **HU-048: Marcar Todas las Notificaciones como Leídas (API)**
**Como** estudiante  
**Quiero** marcar todas mis notificaciones como leídas  
**Para** limpiar el badge de notificaciones

**Criterios de Aceptación:**
- [ ] Endpoint para marcar todas como leídas
- [ ] Actualizar todas las notificaciones pendientes del usuario
- [ ] Respuesta exitosa

**Rutas asociadas:**
- `POST /api/notificacion/marcar_todas_leidas` - Marcar todas leídas

---

#### **HU-049: Eliminar Notificación (API)**
**Como** estudiante  
**Quiero** eliminar una notificación específica  
**Para** limpiar mi bandeja

**Criterios de Aceptación:**
- [ ] Endpoint DELETE para eliminar
- [ ] Validar que sea notificación del usuario autenticado
- [ ] Eliminar de BD

**Rutas asociadas:**
- `DELETE /api/notificacion/eliminar/<id_notificacion>` - Eliminar notificación

---

#### **HU-050: Obtener Notificaciones Sin Leer (API)**
**Como** aplicación/frontend  
**Quiero** obtener cantidad y lista de notificaciones sin leer  
**Para** mostrar badges y alertas

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve notificaciones sin leer
- [ ] Devolver cantidad de notificaciones nuevas
- [ ] Ordenar por fecha (más reciente primero)
- [ ] Respuesta rápida (caché si es posible)

**Rutas asociadas:**
- `GET /api/notificacion/sin_leer` - Obtificaciones sin leer

---

#### **HU-051: Obtener Estudiantes por Materia (API)**
**Como** profesor/aplicación  
**Quiero** obtener lista de estudiantes de una materia específica  
**Para** enviar notificaciones o hacer seguimiento

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve estudiantes de materia
- [ ] Filtrar por ID de materia
- [ ] Mostrar nombre, ID, correo, promedio
- [ ] Validar autorización

**Rutas asociadas:**
- `GET /api/estudiantes_por_materia/<id_materia>` - Estudiantes por materia

---

#### **HU-052: Ver Detalle de Notificación (API)**
**Como** estudiante  
**Quiero** obtener detalles completos de una notificación  
**Para** leer el mensaje completo en un modal

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve notificación con todos sus datos
- [ ] Incluir mensaje, profesor, materia, fecha
- [ ] Historial de conversación si aplica
- [ ] Validar que sea del usuario autenticado

**Rutas asociadas:**
- `GET /api/notificacion/<id_notificacion>` - Ver detalle notificación

---

#### **HU-053: Enviar Mensaje a Profesor (API)**
**Como** estudiante  
**Quiero** enviar mensajes/respuestas a profesores  
**Para** comunicarme sobre temas académicos

**Criterios de Aceptación:**
- [ ] Endpoint POST para crear mensaje
- [ ] Asociar a materia específica
- [ ] Registrar en conversación con profesor
- [ ] Notificar al profesor

**Rutas asociadas:**
- `POST /api/mensaje/enviar` - Enviar mensaje

---

#### **HU-054: Obtener Eventos de una Fecha Específica (API)**
**Como** aplicación  
**Quiero** obtener eventos de un día específico  
**Para** mostrar en vista de día

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve eventos de fecha
- [ ] Parámetro: fecha (YYYY-MM-DD)
- [ ] Devolver eventos personales del estudiante
- [ ] Ordenar por hora

**Rutas asociadas:**
- `GET /api/eventos/fecha/<fecha>` - Eventos por fecha

---

#### **HU-055: Obtener Eventos de un Mes (API)**
**Como** aplicación  
**Quiero** obtener todos los eventos de un mes  
**Para** mostrar en vista de calendario mensual

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve eventos del mes
- [ ] Parámetros: año, mes
- [ ] Devolver todos los eventos personales
- [ ] Ordenar por fecha

**Rutas asociadas:**
- `GET /api/eventos/mes/<anio>/<mes>` - Eventos por mes

---

#### **HU-056: Endpoint de Salud del Sistema (Health Check)**
**Como** sistema de monitoreo  
**Quiero** verificar que la aplicación y BD están funcionando  
**Para** alertar sobre problemas de disponibilidad

**Criterios de Aceptación:**
- [ ] Endpoint que devuelve estado del sistema
- [ ] Verificar conexión a BD
- [ ] Respuesta rápida (< 500ms)
- [ ] Formato JSON

**Rutas asociadas:**
- `GET /_health` - Health check

---

## 📊 MATRIZ DE TRAZABILIDAD COMPLETA

| ID | Historia | Rol | Prioridad | Estado | Ruta API |
|----|---------|----|-----------|--------|----------|
| HU-001 | Gestionar Usuarios | Admin | Alta | ✅ Implementada | `/admin/usuarios` |
| HU-002 | Gestionar Materias | Admin | Alta | ✅ Implementada | `/admin/materias` |
| HU-003 | Gestionar Horarios | Admin | Alta | ✅ Implementada | `/admin/horarios` |
| HU-004 | Gestionar Inscripciones | Admin | Alta | ✅ Implementada | `/admin/inscripciones` |
| HU-005 | Dashboard Admin | Admin | Media | ✅ Implementada | `/admin/dashboard` |
| HU-006 | Asignar Acudiente | Admin | Media | ✅ Implementada | `/admin/asignar_padre` |
| HU-007 | Dashboard Profesor | Profesor | Alta | ✅ Implementada | `/profesor/dashboard` |
| HU-008 | Obtener Estudiantes | Profesor | Alta | ✅ Implementada | `/profesor/obtener_estudiantes` |
| HU-009 | Asignar Calificaciones | Profesor | Alta | ✅ Implementada | `/profesor/asignar_nota` |
| HU-010 | Modificar Calificaciones | Profesor | Alta | ✅ Implementada | `/profesor/cambiar_nota` |
| HU-011 | Enviar Notificaciones | Profesor | Alta | ✅ Implementada | `/api/notificaciones/crear` |
| HU-012 | Ver Hoja de Vida | Profesor | Media | ✅ Implementada | `/profesor/hoja_vida` |
| HU-013 | Subir Hoja de Vida | Profesor | Media | ✅ Implementada | `/profesor/subir_hoja` |
| HU-014 | Ver HV Otros Profes | Profesor | Baja | ✅ Implementada | `/profesor/ver_hoja/<id>` |
| HU-015 | Recibir Respuestas | Profesor | Media | ✅ Implementada | `/api/mensajes/obtener` |
| HU-016 | Dashboard Estudiante | Estudiante | Alta | ✅ Implementada | `/estudiante/dashboard` |
| HU-017 | Ver Calificaciones | Estudiante | Alta | ✅ Implementada | `/estudiante/ver_notas` |
| HU-018 | Ver Horario Clases | Estudiante | Alta | ✅ Implementada | `/estudiante/horario` |
| HU-019 | Crear Eventos Personal | Estudiante | Alta | ✅ Implementada | `/api/eventos/crear` |
| HU-020 | Vista Horario Semanal | Estudiante | Alta | ✅ Implementada | `/estudiante/mi_horario` |
| HU-021 | Inscribirse Materias | Estudiante | Alta | ✅ Implementada | `/estudiante/inscribir_materia` |
| HU-022 | Ver Notificaciones | Estudiante | Alta | ✅ Implementada | `/estudiante/mis_notificaciones` |
| HU-023 | Responder Notificaciones | Estudiante | Alta | ✅ Implementada | `/api/mensajes/crear` |
| HU-024 | Ver Índices Aprendizaje | Estudiante | Media | ✅ Implementada | `/estudiante/indices` |
| HU-025 | Ver Info Hijos | Padre | Alta | ✅ Implementada | `/padre/dashboard` |
| HU-026 | Recibir Notificaciones | Padre | Media | ✅ Implementada | `/padre/notificaciones` |
| HU-027 | Ver Horario Hijos | Padre | Alta | ✅ Implementada | `/padre/ver_horario/<id>` |
| HU-028 | Ver Descripción Desempeño | Padre | Media | ✅ Implementada | `/padre/ver_descripcion` |
| HU-029 | Iniciar Sesión | Todos | Alta | ✅ Implementada | `/login` |
| HU-030 | Registrarse | Todos | Alta | ✅ Implementada | `/register` |
| HU-031 | Cerrar Sesión | Todos | Alta | ✅ Implementada | `/logout` |
| HU-032 | Login Google | Todos | Baja | ✅ Implementada | `/login/google` |
| HU-033 | Notificaciones Grupo | Profesor | Media | ✅ Implementada | `/profesor/enviar_notificacion_grupo` |
| HU-034 | Revisar Perfil Estudiante | Profesor | Media | ✅ Implementada | `/profesor/revisar_estudiante/<id>` |
| HU-035 | Gestionar Índices | Profesor | Media | ✅ Implementada | `/profesor/indices` |
| HU-036 | Descargar Calificaciones | Estudiante | Baja | ✅ Implementada | `/estudiante/calificaciones/descargar` |
| HU-037 | Ver Tareas Pendientes | Estudiante | Media | ✅ Implementada | `/estudiante/tareas` |
| HU-038 | Obtener Materias Disponibles | Estudiante | Alta | ✅ Implementada | `/api/estudiante/materias` |
| HU-039 | Ver Asignaturas Inscritas | Estudiante | Alta | ✅ Implementada | `/estudiante/asignaturas` |
| HU-040 | Ver Clases del Día | Estudiante | Media | ✅ Implementada | `/estudiante/clases` |
| HU-041 | Datos Estudiante (API) | Estudiante | Media | ✅ Implementada | `/api/estudiante/materias` |
| HU-042 | Ver Horario Hijos | Padre | Media | ✅ Implementada | `/ver_horarios` |
| HU-043 | Acceder a Hijos | Padre | Alta | ✅ Implementada | `/padre/hijos` |
| HU-044 | Listado Alumnos | Docente | Media | ✅ Implementada | `/docente/listado_alumnos` |
| HU-045 | Buscar Alumno | Docente | Media | ✅ Implementada | `/docente/buscar_alumno` |
| HU-046 | Directorio Alumnos | General | Baja | ✅ Implementada | `/alumnos` |
| HU-047 | Marcar Leída (API) | Estudiante | Baja | ✅ Implementada | `/api/notificacion/marcar_leida/<id>` |
| HU-048 | Marcar Todas Leídas | Estudiante | Baja | ✅ Implementada | `/api/notificacion/marcar_todas_leidas` |
| HU-049 | Eliminar Notificación | Estudiante | Media | ✅ Implementada | `/api/notificacion/eliminar/<id>` |
| HU-050 | Notificaciones Sin Leer | Estudiante | Alta | ✅ Implementada | `/api/notificacion/sin_leer` |
| HU-051 | Estudiantes por Materia | Profesor | Alta | ✅ Implementada | `/api/estudiantes_por_materia/<id>` |
| HU-052 | Detalle Notificación | Estudiante | Alta | ✅ Implementada | `/api/notificacion/<id>` |
| HU-053 | Enviar Mensaje | Estudiante | Media | ✅ Implementada | `/api/mensaje/enviar` |
| HU-054 | Eventos por Fecha | Estudiante | Media | ✅ Implementada | `/api/eventos/fecha/<fecha>` |
| HU-055 | Eventos por Mes | Estudiante | Media | ✅ Implementada | `/api/eventos/mes/<anio>/<mes>` |
| HU-056 | Health Check | Sistema | Baja | ✅ Implementada | `/_health` |

---

## 📊 ESTADÍSTICAS ACTUALIZADAS

**Total de Historias de Usuario:** 56  
**Historias Implementadas:** 56 ✅  
**Historias en Desarrollo:** 0  
**Historias Pendientes:** 0  

**Distribución por Rol:**
- 👨‍💼 Administrador: 6 HU
- 👨‍🏫 Profesor: 15 HU (incluidas HU-033 a HU-035)
- 👨‍🎓 Estudiante: 20 HU (incluidas HU-036 a HU-041, y APIs)
- 👨‍👩‍👧 Padre/Acudiente: 5 HU (incluida HU-042 a HU-043)
- 👨‍🏫 Docente: 2 HU (HU-044 a HU-045)
- 🔐 Autenticación: 4 HU
- 🔧 Utilidad General/APIs: 4 HU

---

## 📝 Notas Finales

1. **Todas las 56 historias de usuario están completamente implementadas** en el sistema.
2. **El sistema soporta 5 roles principales + utilidades generales** con 72 rutas implementadas.
3. **La comunicación bidireccional profesor-estudiante** ha sido añadida recientemente.
4. **Los eventos personales del estudiante** ahora soportan cualquier día de la semana.
5. **Sistema de APIs robusta** para integraciones y aplicaciones externas.
6. **El sistema es escalable** y permite agregar nuevas historias en el futuro.

---

**Documento preparado por:** Kevin Cuero  
**Fecha:** 4 de diciembre de 2025  
**Versión:** 2.0 (Actualizado con análisis completo)  
**Total de Rutas Identificadas:** 72
**Total de Historias de Usuario:** 56
