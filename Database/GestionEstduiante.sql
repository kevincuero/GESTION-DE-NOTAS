-- Crear la base de datos y usarla
CREATE DATABASE IF NOT EXISTS GestionDeEstudiantes CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE GestionDeEstudiantes;

-- Tabla de administradores
CREATE TABLE IF NOT EXISTS administradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- Tabla de profesores
CREATE TABLE IF NOT EXISTS profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- Tabla de estudiantes (modificada con puede_inscribirse)
CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    puede_inscribirse BOOLEAN DEFAULT FALSE
);

-- Tabla de padres
CREATE TABLE IF NOT EXISTS padres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- Tabla de relación entre padres y estudiantes
CREATE TABLE IF NOT EXISTS padres_estudiantes (
    id_padre INT NOT NULL,
    id_estudiante INT NOT NULL,
    PRIMARY KEY (id_padre, id_estudiante),
    FOREIGN KEY (id_padre) REFERENCES padres(id) ON DELETE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE
);

-- Tabla de materias
CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de asignaciones de profesores a materias
CREATE TABLE IF NOT EXISTS asignaciones (
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    PRIMARY KEY (id_profesor, id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- Tabla de inscripciones de estudiantes a materias
CREATE TABLE IF NOT EXISTS inscripciones (
    id_estudiante INT NOT NULL,
    id_materia INT NOT NULL,
    PRIMARY KEY (id_estudiante, id_materia),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- Tabla de notas (corregida)
CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    nota DECIMAL(5,2) NOT NULL,
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- Tabla de notificaciones (mejorada con relación a profesor)
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

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'profesor', 'estudiante', 'padre') NOT NULL
);

-- Tabla de tareas
CREATE TABLE IF NOT EXISTS tareas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_entrega DATE NOT NULL,
    estado ENUM('pendiente', 'entregada', 'vencida') DEFAULT 'pendiente',
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE
);

-- Tabla de horarios
CREATE TABLE IF NOT EXISTS horarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    dia_semana ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    id_materia INT NOT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- Tabla plantilla de horarios
CREATE TABLE IF NOT EXISTS plantillas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla de mensajes (conversaciones entre estudiantes y profesores)
CREATE TABLE IF NOT EXISTS mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_notificacion INT NOT NULL,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    id_materia INT,
    remitente_tipo ENUM('estudiante', 'profesor') NOT NULL,
    contenido TEXT NOT NULL,
    leido BOOLEAN DEFAULT FALSE,
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

-- Tabla de eventos para estudiantes (Calendario de eventos personalizados)
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
