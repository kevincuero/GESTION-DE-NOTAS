from Config.database_connection import create_connection


class Contenido:
    @staticmethod
    def crear(id_profesor, id_materia, titulo, descripcion, filename, mimetype, tamano, ruta_relativa, tipo='archivo'):
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
            print(f"Error en modelo Contenido.crear: {e}")
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
    def listar(id_profesor=None, id_materia=None):
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
            print(f"Error en modelo Contenido.listar: {e}")
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
    def obtener(id_contenido):
        conexion = create_connection()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contenidos_materia WHERE id = %s", (id_contenido,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en modelo Contenido.obtener: {e}")
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
    def eliminar(id_contenido):
        conexion = create_connection()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ruta, filename FROM contenidos_materia WHERE id = %s", (id_contenido,))
            fila = cursor.fetchone()
            cursor.execute("DELETE FROM contenidos_materia WHERE id = %s", (id_contenido,))
            conexion.commit()
            return fila
        except Exception as e:
            print(f"Error en modelo Contenido.eliminar: {e}")
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
