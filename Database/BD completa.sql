-- Crear la base de datos y usarla
CREATE DATABASE IF NOT EXISTS GestionDeEstudiantes 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_general_ci;

USE GestionDeEstudiantes;

-- -----------------------------------------------------
-- Tabla de administradores
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS administradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- ------------------------------------------------------
-- Tabla de profesores (CORREGIDA: hoja_vida incluida)
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    hoja_vida VARCHAR(255) DEFAULT NULL
);

-- ------------------------------------------------------
-- Tabla de estudiantes
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    puede_inscribirse BOOLEAN DEFAULT FALSE
);

-- ------------------------------------------------------
-- Tabla de padres
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS padres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

-- ------------------------------------------------------
-- Relación padres-estudiantes
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS padres_estudiantes (
    id_padre INT NOT NULL,
    id_estidente INT NOT NULL,
    PRIMARY KEY (id_padre, id_estidente),
    FOREIGN KEY (id_padre) REFERENCES padres(id) ON DELETE CASCADE,
    FOREIGN KEY (id_estidente) REFERENCES estudiantes(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Tabla de materias
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- ------------------------------------------------------
-- Tabla de asignaciones (profesor-materia)
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS asignaciones (
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    PRIMARY KEY (id_profesor, id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Inscripciones estudiantes–materias
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS inscripciones (
    id_estudiante INT NOT NULL,
    id_materia INT NOT NULL,
    PRIMARY KEY (id_estudiante, id_materia),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Tabla de notas
-- ------------------------------------------------------
DROP TABLE IF EXISTS notas;

CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    tipo_evaluacion VARCHAR(50) NOT NULL DEFAULT 'parcial',
    nota DECIMAL(5,2) NOT NULL,
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_evaluacion (id_estudiante, id_materia, tipo_evaluacion, id_profesor),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Tabla de notificaciones
-- ------------------------------------------------------
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
    INDEX idx_leida (leida),
    INDEX idx_fecha (fecha)
);

-- ------------------------------------------------------
-- Tabla de usuarios
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'profesor', 'estudiante', 'padre') NOT NULL
);

-- ------------------------------------------------------
-- Tabla de tareas
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS tareas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_entrega DATE NOT NULL,
    estado ENUM('pendiente', 'entregada', 'vencida') DEFAULT 'pendiente',
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Tabla de horarios
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS horarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_profesor INT NOT NULL,
    dia_semana ENUM('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    id_materia INT NOT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE
);

-- ------------------------------------------------------
-- Tabla plantilla de horarios
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS plantillas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------
-- Índices de Aprendizaje
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS indices_aprendizaje (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_materia INT NOT NULL,
    id_profesor INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500),
    porcentaje DECIMAL(5, 2) NOT NULL DEFAULT 0,
    parcial VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    UNIQUE KEY unique_indice_profesor_materia (id_profesor, id_materia, nombre)
);

-- ------------------------------------------------------
-- Evaluaciones de índices
-- ------------------------------------------------------
CREATE TABLE IF NOT EXISTS evaluaciones_indices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_indice INT NOT NULL,
    id_profesor INT NOT NULL,
    porcentaje_dominio DECIMAL(5, 2) NOT NULL,
    comentario TEXT,
    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_indice) REFERENCES indices_aprendizaje(id) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE
);

CREATE INDEX idx_indices_materia_profesor ON indices_aprendizaje(id_materia, id_profesor);
CREATE INDEX idx_evaluaciones_indice ON evaluaciones_indices(id_indice);
CREATE INDEX idx_evaluaciones_profesor ON evaluaciones_indices(id_profesor);

-- ------------------------------------------------------
-- Tabla de eventos
-- ------------------------------------------------------
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

-- ------------------------------------------------------
-- Tabla de mensajes
-- ------------------------------------------------------
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
