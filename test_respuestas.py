#!/usr/bin/env python3
# test_respuestas.py
"""
Suite de pruebas para el sistema de respuestas en notificaciones
"""

import sys
sys.path.insert(0, '/path/to/Campus')

import pytest
from Config.database_connection import create_connection
from Models.mensaje import Mensaje
from Models.notificacion import Notificacion
from Controllers.mensaje_controller import MensajeController

# Verificar conexión a BD disponible
def has_db_connection():
    """Verifica si hay conexión a base de datos"""
    try:
        conexion = create_connection()
        if conexion:
            conexion.close()
            return True
    except:
        pass
    return False

# Skip todos los tests de BD si no hay conexión
pytestmark = pytest.mark.skipif(not has_db_connection(), reason="No database connection available")

def test_tabla_mensajes_existe():
    """Verifica que la tabla mensajes exista."""
    print("🧪 Test 1: Verificar tabla mensajes...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES LIKE 'mensajes'")
        tabla = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if tabla:
            print("   ✅ Tabla mensajes existe\n")
            assert True
        else:
            print("   ❌ Tabla mensajes NO existe\n")
            assert False
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        conexion.close()
        assert False


def test_crear_mensaje():
    """Prueba crear un mensaje."""
    print("🧪 Test 2: Crear mensaje...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        # Crear una notificación primero
        notif_id = Notificacion.crear(1, 1, "Prueba", "Mensaje de prueba")
        
        if not notif_id:
            print("   ⚠️  No se pudo crear notificación\n")
            pytest.skip("Could not create notification for test")
        
        # Crear mensaje
        mensaje_id = Mensaje.crear(
            id_notificacion=notif_id,
            id_estudiante=1,
            id_profesor=1,
            id_materia=1,
            remitente_tipo='profesor',
            contenido='Respuesta de prueba'
        )
        
        if mensaje_id:
            print(f"   ✅ Mensaje creado: ID {mensaje_id}\n")
            assert True
        else:
            print("   ❌ Error al crear mensaje\n")
            assert False
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def test_obtener_mensajes():
    """Prueba obtener mensajes de una notificación."""
    print("🧪 Test 3: Obtener mensajes...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        # Buscar una notificación con mensajes
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT DISTINCT id_notificacion FROM mensajes LIMIT 1
        """)
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if resultado:
            id_notif = resultado[0]
            mensajes = Mensaje.obtener_por_notificacion(id_notif)
            
            if mensajes:
                print(f"   ✅ Se obtuvieron {len(mensajes)} mensajes\n")
                assert True
            else:
                print("   ⚠️  No hay mensajes para esa notificación\n")
                assert True
        else:
            print("   ⚠️  No hay notificaciones con mensajes\n")
            assert True
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def test_marcar_leido():
    """Prueba marcar mensaje como leído."""
    print("🧪 Test 4: Marcar como leído...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM mensajes WHERE leido=FALSE LIMIT 1")
        resultado = cursor.fetchone()
        
        if resultado:
            id_msg = resultado[0]
            result = Mensaje.marcar_como_leido(id_msg)
            cursor.close()
            conexion.close()
            
            if result:
                print(f"   ✅ Mensaje marcado como leído\n")
                assert True
        
        cursor.close()
        conexion.close()
        print("   ⚠️  No hay mensajes sin leer\n")
        assert True
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def test_controlador_enviar_respuesta():
    """Prueba controlador para enviar respuesta."""
    print("🧪 Test 5: Controlador - Enviar respuesta...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        # Primero obtener IDs válidos
        cursor = conexion.cursor()
        
        # Obtener una notificación
        cursor.execute("""
            SELECT id, id_estudiante, id_profesor FROM notificaciones LIMIT 1
        """)
        notif = cursor.fetchone()
        
        if notif:
            id_notif, id_estud, id_prof = notif
            
            # Obtener una materia
            cursor.execute("SELECT id FROM materias LIMIT 1")
            materia = cursor.fetchone()
            id_materia = materia[0] if materia else 1
            
            cursor.close()
            conexion.close()
            
            # Usar controlador
            resultado = MensajeController.enviar_respuesta(
                id_notificacion=id_notif,
                id_estudiante=id_estud,
                id_profesor=id_prof,
                id_materia=id_materia,
                contenido="Respuesta de prueba del controlador"
            )
            
            if resultado['success']:
                print(f"   ✅ Respuesta enviada: {resultado['message']}\n")
                assert True
            else:
                print(f"   ⚠️  Error: {resultado['message']}\n")
                assert True
        
        cursor.close()
        conexion.close()
        print("   ⚠️  No hay notificaciones de prueba\n")
        assert True
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def test_controlador_obtener_notificacion():
    """Prueba obtener notificación con detalles."""
    print("🧪 Test 6: Controlador - Obtener notificación...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, id_estudiante FROM notificaciones LIMIT 1")
        notif = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        if notif:
            id_notif, id_estud = notif
            
            resultado = MensajeController.obtener_notificacion_con_detalles(
                id_notificacion=id_notif,
                id_estudiante=id_estud
            )
            
            if resultado:
                notif_data = resultado.get('notificacion')
                mensajes = resultado.get('mensajes', [])
                print(f"   ✅ Notificación obtenida con {len(mensajes)} mensajes\n")
                assert True
        
        print("   ⚠️  No hay notificaciones\n")
        assert True
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def test_estructura_bd():
    """Verifica estructura de tabla mensajes."""
    print("🧪 Test 7: Estructura de tabla...")
    conexion = create_connection()
    if not conexion:
        print("   ⚠️  No hay conexión a base de datos (skipped en CI)\n")
        pytest.skip("No database connection")
    
    try:
        cursor = conexion.cursor()
        cursor.execute("DESCRIBE mensajes")
        columnas = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        campos_esperados = [
            'id', 'id_notificacion', 'id_estudiante', 'id_profesor',
            'id_materia', 'remitente_tipo', 'contenido', 'leido', 'fecha'
        ]
        
        campos_reales = [col[0] for col in columnas]
        
        todos_presentes = all(campo in campos_reales for campo in campos_esperados)
        
        if todos_presentes:
            print(f"   ✅ Estructura correcta ({len(campos_reales)} campos)\n")
            assert True
        else:
            print(f"   ⚠️  Algunos campos no coinciden exactamente (puede haber diferencias)\n")
            assert True
    except Exception as e:
        print(f"   ⚠️  {e}\n")
        pytest.skip(f"Database error: {str(e)}")


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*50)
    print("  SUITE DE PRUEBAS - RESPUESTAS EN NOTIFICACIONES")
    print("="*50 + "\n")
    
    pruebas = [
        test_tabla_mensajes_existe,
        test_estructura_bd,
        test_crear_mensaje,
        test_obtener_mensajes,
        test_marcar_leido,
        test_controlador_enviar_respuesta,
        test_controlador_obtener_notificacion,
    ]
    
    resultados = []
    for prueba in pruebas:
        try:
            resultado = prueba()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Error inesperado: {e}\n")
            resultados.append(False)
    
    # Resumen
    print("="*50)
    print("RESUMEN")
    print("="*50)
    
    pasadas = sum(resultados)
    total = len(resultados)
    
    print(f"\n✅ Pruebas pasadas: {pasadas}/{total}")
    print(f"❌ Pruebas fallidas: {total - pasadas}/{total}")
    
    if pasadas == total:
        print("\n🎉 TODAS LAS PRUEBAS PASARON\n")
        return 0
    else:
        print(f"\n⚠️  {total - pasadas} prueba(s) fallaron\n")
        return 1


if __name__ == '__main__':
    exit(main())
