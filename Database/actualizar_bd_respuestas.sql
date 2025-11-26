-- Database/actualizar_bd_respuestas.sql
-- Script de migración para agregar tabla de mensajes

USE GestionDeEstudiantes;

-- Verificar si la tabla ya existe antes de crearla
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Confirmar creación
SELECT 'Tabla mensajes creada exitosamente' AS estado;
SELECT COUNT(*) as total_tablas FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'GestionDeEstudiantes' AND TABLE_NAME = 'mensajes';
