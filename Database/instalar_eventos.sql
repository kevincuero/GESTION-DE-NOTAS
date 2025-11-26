-- ===============================================================
-- Script de Instalación del Sistema de Eventos
-- Ejecutar este script en tu base de datos MySQL
-- ===============================================================

USE GestionDeEstudiantes;

-- Crear tabla de eventos si no existe
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

-- Verificar que la tabla se creó correctamente
SELECT 'Tabla de eventos creada exitosamente' AS mensaje;

-- Mostrar estructura de la tabla
DESCRIBE eventos;

-- Si necesitas borrar la tabla (CUIDADO - borrará todos los eventos):
-- DROP TABLE IF EXISTS eventos;
