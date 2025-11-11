from Config.database_connection import create_connection
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ProfesorController:
    @staticmethod
    def obtener_materias_asignadas(id_profesor):
        """Obtiene las materias asignadas a un profesor."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.id, m.nombre 
                FROM materias m
                INNER JOIN asignaciones a ON m.id = a.id_materia
                WHERE a.id_profesor = %s
                """
                cursor.execute(query, (id_profesor,))
                materias = cursor.fetchall()
                return materias
            except Error as e:
                print(f"Error al obtener materias asignadas: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

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
    def asignar_nota(id_estudiante, id_profesor, id_materia, nota, comentario):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Asegúrate de convertir los datos a los tipos correctos
                id_estudiante = int(id_estudiante)
                id_profesor = int(id_profesor)
                id_materia = int(id_materia)
                nota = float(nota)
                comentario = str(comentario)

                # Verifica si ya existe una nota para el estudiante, profesor y materia
                cursor.execute("""
                    SELECT id FROM notas
                    WHERE id_estudiante=%s AND id_profesor=%s AND id_materia=%s
                """, (id_estudiante, id_profesor, id_materia))
                existe = cursor.fetchone()
                if existe:
                    # Si existe, se actualiza la nota
                    cursor.execute("""
                        UPDATE notas SET nota=%s, comentario=%s
                        WHERE id_estudiante=%s AND id_profesor=%s AND id_materia=%s
                    """, (nota, comentario, id_estudiante, id_profesor, id_materia))
                else:
                    # Si no existe, inserta una nueva nota
                    cursor.execute("""
                        INSERT INTO notas (id_estudiante, id_profesor, id_materia, nota, comentario)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_estudiante, id_profesor, id_materia, nota, comentario))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al asignar nota: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False
        

    @staticmethod
    def cambiar_nota(id_estudiante, id_materia, nueva_nota, comentario, id_profesor):
        """Cambia la nota y el comentario de un estudiante en una materia específica."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE notas
                    SET nota=%s, comentario=%s
                    WHERE id_estudiante=%s AND id_materia=%s AND id_profesor=%s
                """, (nueva_nota, comentario, id_estudiante, id_materia, id_profesor))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al cambiar nota: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False
    

    @staticmethod
    def enviar_notificacion(correo, asunto, mensaje):
        """Envía una notificación por correo electrónico a un estudiante."""
        # Aquí puedes usar una librería como smtplib para enviar correos electrónicos.
        try:
            print(f"Enviando correo a {correo}...")
            print(f"Asunto: {asunto}")
            print(f"Mensaje: {mensaje}")
            # Lógica para enviar correo (smtplib, etc.)
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {e}")


    @staticmethod
    def enviar_notificacion(correo_padre, asunto, mensaje):
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