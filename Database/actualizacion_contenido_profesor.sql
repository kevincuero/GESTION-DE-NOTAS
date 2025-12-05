-- ============================================================================
-- Tabla para rastrear actualizaciones de contenido por profesor-materia
-- Esta tabla registra la última actualización de contenido (subida/edición)
-- Se utiliza para generar notificaciones cada 3 días sin actualización
-- ============================================================================

CREATE TABLE IF NOT EXISTS profesor_actualizaciones_contenido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT NOT NULL,
    id_materia INT NOT NULL,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notificacion_enviada BOOLEAN DEFAULT FALSE,
    fecha_notificacion TIMESTAMP NULL,
    UNIQUE KEY unique_profesor_materia (id_profesor, id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES materias(id) ON DELETE CASCADE,
    INDEX idx_profesor_materia (id_profesor, id_materia),
    INDEX idx_ultima_actualizacion (ultima_actualizacion),
    INDEX idx_notificacion_enviada (notificacion_enviada)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ============================================================================
-- Trigger para actualizar automáticamente cuando se suba contenido
-- ============================================================================
DELIMITER $$

DROP TRIGGER IF EXISTS actualizar_contenido_profesor_insert$$

CREATE TRIGGER actualizar_contenido_profesor_insert
AFTER INSERT ON contenidos_materia
FOR EACH ROW
BEGIN
    INSERT INTO profesor_actualizaciones_contenido (id_profesor, id_materia, ultima_actualizacion, notificacion_enviada)
    VALUES (NEW.id_profesor, NEW.id_materia, CURRENT_TIMESTAMP, FALSE)
    ON DUPLICATE KEY UPDATE
        ultima_actualizacion = CURRENT_TIMESTAMP,
        notificacion_enviada = FALSE,
        fecha_notificacion = NULL;
END$$

DROP TRIGGER IF EXISTS actualizar_contenido_profesor_update$$

CREATE TRIGGER actualizar_contenido_profesor_update
AFTER UPDATE ON contenidos_materia
FOR EACH ROW
BEGIN
    INSERT INTO profesor_actualizaciones_contenido (id_profesor, id_materia, ultima_actualizacion, notificacion_enviada)
    VALUES (NEW.id_profesor, NEW.id_materia, CURRENT_TIMESTAMP, FALSE)
    ON DUPLICATE KEY UPDATE
        ultima_actualizacion = CURRENT_TIMESTAMP,
        notificacion_enviada = FALSE,
        fecha_notificacion = NULL;
END$$

DELIMITER ;

-- ============================================================================
-- Procedimiento almacenado para verificar y crear notificaciones
-- Se ejecuta periódicamente (ej: cada hora o cada vez que el profesor entra)
-- ============================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS generar_notificaciones_contenido_vencido$$

CREATE PROCEDURE generar_notificaciones_contenido_vencido()
BEGIN
    DECLARE v_id_profesor INT;
    DECLARE v_id_materia INT;
    DECLARE v_materia_nombre VARCHAR(100);
    DECLARE done INT DEFAULT FALSE;
    DECLARE cursor_profesores CURSOR FOR
        SELECT pac.id_profesor, pac.id_materia, m.nombre
        FROM profesor_actualizaciones_contenido pac
        JOIN materias m ON pac.id_materia = m.id
        WHERE pac.notificacion_enviada = FALSE
        AND DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)) >= 3;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cursor_profesores;

    leer_registros: LOOP
        FETCH cursor_profesores INTO v_id_profesor, v_id_materia, v_materia_nombre;
        IF done THEN
            LEAVE leer_registros;
        END IF;

        -- Crear notificación para el profesor
        INSERT INTO notificaciones (
            id_profesor,
            id_estudiante,
            titulo,
            mensaje,
            leida,
            fecha
        ) VALUES (
            v_id_profesor,
            NULL,  -- NULL porque es notificación al profesor, no a un estudiante específico
            CONCAT('Contenido desactualizado: ', v_materia_nombre),
            CONCAT(
                'Hace más de 3 días no actualizas el contenido de la materia "',
                v_materia_nombre,
                '". Por favor, sube material actualizado para mantener a tus estudiantes informados.'
            ),
            FALSE,
            CURRENT_TIMESTAMP
        );

        -- Marcar como enviada
        UPDATE profesor_actualizaciones_contenido
        SET notificacion_enviada = TRUE,
            fecha_notificacion = CURRENT_TIMESTAMP
        WHERE id_profesor = v_id_profesor
        AND id_materia = v_id_materia;

    END LOOP;

    CLOSE cursor_profesores;

END$$

DELIMITER ;

-- ============================================================================
-- Función auxiliar para obtener días desde la última actualización
-- ============================================================================
DELIMITER $$

DROP FUNCTION IF EXISTS dias_sin_actualizar$$

CREATE FUNCTION dias_sin_actualizar(p_id_profesor INT, p_id_materia INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_dias INT;
    SELECT DATEDIFF(CURDATE(), DATE(ultima_actualizacion))
    INTO v_dias
    FROM profesor_actualizaciones_contenido
    WHERE id_profesor = p_id_profesor AND id_materia = p_id_materia;
    
    RETURN COALESCE(v_dias, 0);
END$$

DELIMITER ;

-- ============================================================================
-- Ejemplo de uso en una consulta para mostrar en el dashboard del profesor
-- ============================================================================
-- SELECT 
--     m.id,
--     m.nombre,
--     pac.ultima_actualizacion,
--     dias_sin_actualizar(?, m.id) as dias_sin_actualizar,
--     CASE 
--         WHEN dias_sin_actualizar(?, m.id) >= 3 THEN 'URGENTE'
--         WHEN dias_sin_actualizar(?, m.id) >= 2 THEN 'ALERTA'
--         ELSE 'ACTUALIZADO'
--     END as estado_contenido
-- FROM asignaciones a
-- JOIN materias m ON a.id_materia = m.id
-- LEFT JOIN profesor_actualizaciones_contenido pac ON a.id_profesor = pac.id_profesor AND a.id_materia = pac.id_materia
-- WHERE a.id_profesor = ?
-- ORDER BY dias_sin_actualizar(?, m.id) DESC;
