-- Script de Actualización de Base de Datos
-- Para migrar a la nueva estructura de notificaciones
-- Ejecutar este script ANTES de usar el sistema de notificaciones

USE GestionDeEstudiantes;

-- Paso 1: Crear tabla de notificaciones mejorada (si no existe)
-- Si existe, se mantendrá intacta
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Verificar datos
SELECT 'Total de notificaciones:' as Descripcion, COUNT(*) as Cantidad FROM notificaciones;
SELECT 'No leídas:' as Descripcion, COUNT(*) as Cantidad FROM notificaciones WHERE leida = FALSE;

-- Fin de script
COMMIT;
