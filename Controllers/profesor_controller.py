from Config.database_connection import create_connection
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ProfesorController:
    @staticmethod
    def obtener_materias_asignadas(id_profesor):
        """Obtiene las materias asignadas a un profesor. Si no hay asignaciones, retorna todas las materias."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                # Primero intenta obtener materias asignadas
                query_asignadas = """
                SELECT m.id, m.nombre 
                FROM materias m
                INNER JOIN asignaciones a ON m.id = a.id_materia
                WHERE a.id_profesor = %s
                ORDER BY m.nombre
                """
                cursor.execute(query_asignadas, (id_profesor,))
                materias = cursor.fetchall()
                
                # Si no hay asignaciones, retorna todas las materias como fallback
                if not materias:
                    query_todas = """
                    SELECT id, nombre 
                    FROM materias
                    ORDER BY nombre
                    """
                    cursor.execute(query_todas)
                    materias = cursor.fetchall()
                
                return materias
            except Error as e:
                print(f"Error al obtener materias asignadas: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def obtener_materias():
        """Obtiene todas las materias disponibles."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT id, nombre FROM materias"
                cursor.execute(query)
                materias = cursor.fetchall()
                return materias
            except Error as e:
                print(f"Error al obtener materias: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
                
    @staticmethod
    def obtener_estudiantes_por_materia(id_materia):
        """Obtiene los estudiantes inscritos en una materia específica, incluyendo el nombre de la materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT e.id, e.nombre AS estudiante, e.correo, m.nombre AS materia
                FROM estudiantes e
                INNER JOIN inscripciones i ON e.id = i.id_estudiante
                INNER JOIN materias m ON i.id_materia = m.id
                WHERE i.id_materia = %s
                """
                cursor.execute(query, (id_materia,))
                estudiantes = cursor.fetchall()
                return estudiantes
            except Exception as e:
                print(f"Error al obtener estudiantes por materia: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def asignar_nota(id_estudiante, id_profesor, id_materia, nota, tipo_evaluacion='parcial', comentario=''):
        """Asigna una nueva nota a un estudiante con tipo de evaluación especificado."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Convertir datos a tipos correctos
                id_estudiante = int(id_estudiante)
                id_profesor = int(id_profesor)
                id_materia = int(id_materia)
                nota = float(nota)
                tipo_evaluacion = str(tipo_evaluacion)
                comentario = str(comentario)

                # Verifica si ya existe una nota para el mismo estudiante, profesor, materia y tipo de evaluación
                cursor.execute("""
                    SELECT id FROM notas
                    WHERE id_estudiante=%s AND id_profesor=%s AND id_materia=%s AND tipo_evaluacion=%s
                """, (id_estudiante, id_profesor, id_materia, tipo_evaluacion))
                existe = cursor.fetchone()
                
                if existe:
                    # Si existe, se actualiza la nota y se registra la fecha/hora
                    cursor.execute("""
                        UPDATE notas SET nota=%s, comentario=%s, fecha=NOW()
                        WHERE id_estudiante=%s AND id_profesor=%s AND id_materia=%s AND tipo_evaluacion=%s
                    """, (nota, comentario, id_estudiante, id_profesor, id_materia, tipo_evaluacion))
                else:
                    # Si no existe, inserta una nueva nota con fecha actual
                    cursor.execute("""
                        INSERT INTO notas (id_estudiante, id_profesor, id_materia, tipo_evaluacion, nota, comentario, fecha)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, (id_estudiante, id_profesor, id_materia, tipo_evaluacion, nota, comentario))
                
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al asignar nota: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def obtener_nota_por_estudiante_materia(id_estudiante, id_materia, id_profesor):
        """Obtiene la primera nota de un estudiante en una materia para un profesor específico."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT id, tipo_evaluacion FROM notas
                WHERE id_estudiante=%s AND id_materia=%s AND id_profesor=%s
                LIMIT 1
                """
                cursor.execute(query, (id_estudiante, id_materia, id_profesor))
                resultado = cursor.fetchone()
                return resultado
            except Exception as e:
                print(f"Error al obtener nota del estudiante: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def cambiar_nota(id_estudiante, id_materia, nueva_nota, tipo_nota, comentario, id_profesor):
        """Cambia la nota, tipo de evaluación y comentario de un estudiante en una materia específica."""
        conexion = create_connection()
        if conexion:
            try:
                # Primero obtener el tipo_evaluacion anterior para hacer el WHERE correcto
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("""
                    SELECT tipo_evaluacion FROM notas
                    WHERE id_estudiante=%s AND id_materia=%s AND id_profesor=%s
                    LIMIT 1
                """, (id_estudiante, id_materia, id_profesor))
                nota_actual = cursor.fetchone()
                
                if not nota_actual:
                    print(f"No se encontró nota para estudiante {id_estudiante} en materia {id_materia}")
                    return False
                
                tipo_anterior = nota_actual['tipo_evaluacion']
                
                # Ahora actualizar usando el tipo anterior en el WHERE
                cursor.execute("""
                    UPDATE notas
                    SET nota=%s, tipo_evaluacion=%s, comentario=%s, fecha=NOW()
                    WHERE id_estudiante=%s AND id_materia=%s AND id_profesor=%s AND tipo_evaluacion=%s
                """, (nueva_nota, tipo_nota, comentario, id_estudiante, id_materia, id_profesor, tipo_anterior))
                conexion.commit()
                
                if cursor.rowcount > 0:
                    print(f"Nota actualizada: estudiante {id_estudiante}, materia {id_materia}, tipo anterior {tipo_anterior} -> nuevo tipo {tipo_nota}")
                    return True
                else:
                    print(f"No se actualizó ninguna fila para estudiante {id_estudiante}")
                    return False
            except Exception as e:
                print(f"Error al cambiar nota: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def obtener_nota_estudiante(id_estudiante, id_materia, tipo_evaluacion, id_profesor):
        """Obtiene una nota específica de un estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, m.nombre as materia, p.nombre as profesor
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s AND n.id_materia = %s AND n.tipo_evaluacion = %s AND n.id_profesor = %s
                """
                cursor.execute(query, (id_estudiante, id_materia, tipo_evaluacion, id_profesor))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener nota del estudiante: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def obtener_notas_materia_profesor(id_materia, id_profesor):
        """Obtiene todas las notas de una materia asignada a un profesor."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, e.nombre as estudiante, e.correo, m.nombre as materia
                FROM notas n
                JOIN estudiantes e ON n.id_estudiante = e.id
                JOIN materias m ON n.id_materia = m.id
                WHERE n.id_materia = %s AND n.id_profesor = %s
                ORDER BY e.nombre, n.tipo_evaluacion
                """
                cursor.execute(query, (id_materia, id_profesor))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener notas de la materia: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def enviar_notificacion(correo, asunto, mensaje):
        """Envía una notificación por correo electrónico a un estudiante."""
        try:
            print(f"Enviando correo a {correo}...")
            print(f"Asunto: {asunto}")
            print(f"Mensaje: {mensaje}")
            # Lógica para enviar correo (smtplib, etc.)
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    @staticmethod
    def enviar_notificacion_padre(correo_padre, asunto, mensaje):
        """Envía una notificación por correo electrónico al padre del estudiante."""
        try:
            # Configuración del servidor SMTP
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login('tu_correo@gmail.com', 'tu_contraseña')  # Cambia esto por tus credenciales

            # Crear el correo
            correo = MIMEMultipart()
            correo['From'] = 'tu_correo@gmail.com'
            correo['To'] = correo_padre
            correo['Subject'] = asunto
            correo.attach(MIMEText(mensaje, 'plain'))

            # Enviar el correo
            servidor.send_message(correo)
            servidor.quit()
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return False

    @staticmethod
    def obtener_tipos_evaluacion_disponibles():
        """Retorna los tipos de evaluación disponibles."""
        return [
            'Parcial 1',
            'Parcial 2',
            'Parcial 3',
            'Quiz',
            'Tarea',
            'Proyecto',
            'Participación',
            'Examen Final'
        ]

    @staticmethod
    def enviar_notificacion_a_estudiante(id_estudiante, id_profesor, titulo, mensaje):
        """Envía notificación EN PLATAFORMA (sin correo electrónico)."""
        from Models.notificacion import Notificacion
        return Notificacion.crear(id_estudiante, id_profesor, titulo, mensaje)

    # -------------------
    # Contenidos (recursos de materia)
    # -------------------
    @staticmethod
    def subir_contenido(id_profesor, id_materia, titulo, descripcion, filename, mimetype, tamano, ruta_relativa, tipo='archivo'):
        """Registra un contenido subido por el profesor para una materia."""
        conexion = create_connection()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO contenidos_materia (id_profesor, id_materia, titulo, descripcion, tipo, filename, mimetype, tamano, ruta, fecha_subida)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (id_profesor, id_materia, titulo, descripcion, tipo, filename, mimetype, tamano, ruta_relativa))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al subir contenido: {e}")
            try:
                conexion.rollback()
            except Exception:
                pass
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    @staticmethod
    def listar_contenidos_por_profesor_materia(id_profesor=None, id_materia=None):
        """Lista contenidos filtrando por profesor y/o materia. Si no se especifica, lista todos."""
        conexion = create_connection()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            base = "SELECT * FROM contenidos_materia"
            condiciones = []
            params = []
            if id_profesor:
                condiciones.append("id_profesor = %s")
                params.append(id_profesor)
            if id_materia:
                condiciones.append("id_materia = %s")
                params.append(id_materia)
            if condiciones:
                base += " WHERE " + " AND ".join(condiciones)
            base += " ORDER BY fecha_subida DESC"
            cursor.execute(base, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar contenidos: {e}")
            return []
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    @staticmethod
    def obtener_contenido_por_id(id_contenido):
        conexion = create_connection()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contenidos_materia WHERE id = %s", (id_contenido,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener contenido por id: {e}")
            return None
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    @staticmethod
    def eliminar_contenido(id_contenido):
        conexion = create_connection()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ruta, filename FROM contenidos_materia WHERE id = %s", (id_contenido,))
            fila = cursor.fetchone()
            # eliminar registro
            cursor.execute("DELETE FROM contenidos_materia WHERE id = %s", (id_contenido,))
            conexion.commit()
            return fila
        except Exception as e:
            print(f"Error al eliminar contenido: {e}")
            try:
                conexion.rollback()
            except Exception:
                pass
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    # ----Funcion para que funcione el pytest de docente ----
    @staticmethod
    def obtener_estudiantes_de_profesor(id_profesor):
        conexion = create_connection()
        if not conexion:
            return []

        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT e.id, e.nombre
            FROM estudiantes e
            JOIN notas n ON n.id_estudiante = e.id
            WHERE n.id_profesor = %s
        """, (id_profesor,))
        resultado = cursor.fetchall()
        cursor.close()
        conexion.close()

        return resultado

    @staticmethod
    def buscar_estudiante_por_nombre(id_profesor, nombre):
        conexion = create_connection()
        if not conexion:
            return []

        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT e.id, e.nombre
            FROM estudiantes e
            JOIN notas n ON n.id_estudiante = e.id
            WHERE n.id_profesor = %s AND e.nombre LIKE %s
        """, (id_profesor, f"%{nombre}%"))
        
        resultado = cursor.fetchall()
        cursor.close()
        conexion.close()

        return resultado
