-- Script para crear las tablas de Índices de Aprendizaje
-- Ejecutar después de crear la base de datos principal

USE GestionDeEstudiantes;

-- Tabla de Índices de Aprendizaje
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

-- Tabla de Evaluaciones de Índices (evaluación grupal)
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

-- Índices para mejorar el rendimiento
CREATE INDEX idx_indices_materia_profesor ON indices_aprendizaje(id_materia, id_profesor);
CREATE INDEX idx_evaluaciones_indice ON evaluaciones_indices(id_indice);
CREATE INDEX idx_evaluaciones_profesor ON evaluaciones_indices(id_profesor);
