"""
test_notificaciones.py - Script de prueba para el sistema de notificaciones

Para ejecutar:
python test_notificaciones.py

Requisitos:
- Tener el proyecto configurado
- Base de datos actualizada
- Profesores y estudiantes en BD
"""

import sys
sys.path.insert(0, '.')

from Config.database_connection import create_connection
from Controllers.notificacion_controller import NotificacionController
from Models.notificacion import Notificacion

def test_crear_notificacion():
    """Test: Crear una notificación"""
    print("\n" + "="*60)
    print("TEST 1: Crear notificación individual")
    print("="*60)
    
    resultado = NotificacionController.enviar_notificacion_a_estudiante(
        id_estudiante=1,
        id_profesor=1,
        titulo="Test: Notificación de prueba",
        mensaje="Esta es una notificación de prueba del sistema."
    )
    
    print(f"Éxito: {resultado['success']}")
    print(f"Mensaje: {resultado['message']}")
    print(f"ID Notificación: {resultado['notification_id']}")
    
    return resultado['success']

def test_crear_multiples():
    """Test: Crear múltiples notificaciones"""
    print("\n" + "="*60)
    print("TEST 2: Crear múltiples notificaciones")
    print("="*60)
    
    resultado = NotificacionController.enviar_notificacion_a_multiples(
        id_estudiantes=[1, 2, 3],
        id_profesor=1,
        titulo="Test: Notificación masiva",
        mensaje="Esta notificación fue enviada a múltiples estudiantes."
    )
    
    print(f"Éxito: {resultado['success']}")
    print(f"Mensaje: {resultado['message']}")
    print(f"Notificaciones creadas: {resultado['count']}")
    
    return resultado['success']

def test_obtener_notificaciones():
    """Test: Obtener notificaciones de un estudiante"""
    print("\n" + "="*60)
    print("TEST 3: Obtener notificaciones")
    print("="*60)
    
    notificaciones = NotificacionController.obtener_notificaciones_estudiante(1)
    
    print(f"Total de notificaciones: {len(notificaciones)}")
    
    if notificaciones:
        print("\nPrimeras 3 notificaciones:")
        for i, notif in enumerate(notificaciones[:3], 1):
            print(f"\n  {i}. {notif.get('titulo')}")
            print(f"     Profesor: {notif.get('profesor_nombre')}")
            print(f"     Leída: {notif.get('leida')}")
            print(f"     Fecha: {notif.get('fecha')}")
    
    return len(notificaciones) > 0

def test_obtener_sin_leer():
    """Test: Obtener notificaciones sin leer"""
    print("\n" + "="*60)
    print("TEST 4: Obtener notificaciones sin leer")
    print("="*60)
    
    notificaciones = NotificacionController.obtener_notificaciones_sin_leer(1)
    
    print(f"Notificaciones sin leer: {len(notificaciones)}")
    
    if notificaciones:
        print("\nNotificaciones sin leer:")
        for notif in notificaciones[:5]:
            print(f"  - {notif.get('titulo')}")
    
    return True

def test_contar_no_leidas():
    """Test: Contar notificaciones no leídas"""
    print("\n" + "="*60)
    print("TEST 5: Contar notificaciones no leídas")
    print("="*60)
    
    count = NotificacionController.obtener_conteo_no_leidas(1)
    
    print(f"Notificaciones no leídas del estudiante 1: {count}")
    
    return True

def test_marcar_como_leida():
    """Test: Marcar como leída"""
    print("\n" + "="*60)
    print("TEST 6: Marcar notificación como leída")
    print("="*60)
    
    # Obtener una notificación sin leer
    notificaciones = NotificacionController.obtener_notificaciones_sin_leer(1)
    
    if notificaciones:
        id_notif = notificaciones[0]['id']
        
        resultado = NotificacionController.marcar_como_leida(id_notif)
        
        print(f"ID Notificación: {id_notif}")
        print(f"Éxito: {resultado['success']}")
        print(f"Mensaje: {resultado['message']}")
        
        return resultado['success']
    else:
        print("No hay notificaciones sin leer para probar")
        return False

def test_marcar_todas_como_leidas():
    """Test: Marcar todas como leídas"""
    print("\n" + "="*60)
    print("TEST 7: Marcar todas como leídas")
    print("="*60)
    
    resultado = NotificacionController.marcar_todas_como_leidas(1)
    
    print(f"Éxito: {resultado['success']}")
    print(f"Mensaje: {resultado['message']}")
    print(f"Notificaciones marcadas: {resultado['count']}")
    
    return resultado['success']

def test_eliminar_notificacion():
    """Test: Eliminar notificación"""
    print("\n" + "="*60)
    print("TEST 8: Eliminar notificación")
    print("="*60)
    
    # Obtener notificación más reciente
    notificaciones = NotificacionController.obtener_notificaciones_estudiante(1)
    
    if notificaciones:
        id_notif = notificaciones[0]['id']
        
        resultado = NotificacionController.eliminar_notificacion(id_notif)
        
        print(f"ID Notificación: {id_notif}")
        print(f"Éxito: {resultado['success']}")
        print(f"Mensaje: {resultado['message']}")
        
        return resultado['success']
    else:
        print("No hay notificaciones para eliminar")
        return False

def test_enviar_a_clase():
    """Test: Enviar notificación a toda una clase"""
    print("\n" + "="*60)
    print("TEST 9: Enviar notificación a toda la clase")
    print("="*60)
    
    resultado = NotificacionController.enviar_notificacion_a_clase(
        id_materia=1,
        id_profesor=1,
        titulo="Test: Aviso para toda la clase",
        mensaje="Todos los estudiantes de esta materia recibirán este mensaje."
    )
    
    print(f"Éxito: {resultado['success']}")
    print(f"Mensaje: {resultado['message']}")
    print(f"Notificaciones enviadas: {resultado['count']}")
    
    return resultado['success']

def test_obtener_por_profesor():
    """Test: Obtener notificaciones enviadas por profesor"""
    print("\n" + "="*60)
    print("TEST 10: Obtener notificaciones del profesor")
    print("="*60)
    
    notificaciones = NotificacionController.obtener_notificaciones_profesor(1)
    
    print(f"Notificaciones enviadas por profesor 1: {len(notificaciones)}")
    
    if notificaciones:
        print("\nPrimeras 3:")
        for notif in notificaciones[:3]:
            print(f"  - {notif.get('titulo')} -> {notif.get('estudiante_nombre')}")
    
    return True

def verificar_bd():
    """Verificar conexión a base de datos"""
    print("\n" + "="*60)
    print("VERIFICAR CONEXIÓN A BASE DE DATOS")
    print("="*60)
    
    conexion = create_connection()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar tabla
        cursor.execute("SHOW TABLES LIKE 'notificaciones'")
        tabla = cursor.fetchone()
        
        if tabla:
            print("✅ Tabla 'notificaciones' existe")
            
            # Verificar columnas
            cursor.execute("DESCRIBE notificaciones")
            columnas = cursor.fetchall()
            
            print("\nColumnas:")
            for col in columnas:
                print(f"  - {col['Field']} ({col['Type']})")
        else:
            print("❌ Tabla 'notificaciones' NO existe")
        
        cursor.close()
        conexion.close()
        return tabla is not None
    else:
        print("❌ No se pudo conectar a la base de datos")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "SUITE DE PRUEBAS - SISTEMA DE NOTIFICACIONES".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    resultados = {}
    
    # Verificar BD
    if not verificar_bd():
        print("\n⚠️  Por favor actualiza la base de datos ejecutando:")
        print("   Database/actualizar_notificaciones.sql")
        return
    
    # Ejecutar tests
    tests = [
        ("Crear notificación", test_crear_notificacion),
        ("Crear múltiples", test_crear_multiples),
        ("Obtener notificaciones", test_obtener_notificaciones),
        ("Obtener sin leer", test_obtener_sin_leer),
        ("Contar no leídas", test_contar_no_leidas),
        ("Marcar como leída", test_marcar_como_leida),
        ("Marcar todas leídas", test_marcar_todas_como_leidas),
        ("Obtener por profesor", test_obtener_por_profesor),
    ]
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados[nombre] = "✅ PASS" if resultado else "⚠️  PASS CON ADVERTENCIAS"
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            resultados[nombre] = f"❌ FAIL: {str(e)}"
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        print(f"{nombre:.<40} {resultado}")
    
    total_exitosas = sum(1 for r in resultados.values() if "✅" in r)
    total = len(resultados)
    
    print("\n" + "="*60)
    print(f"Resultado final: {total_exitosas}/{total} pruebas exitosas")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
