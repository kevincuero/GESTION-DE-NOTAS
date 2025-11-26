"""
Script de validación del Sistema de Índices de Aprendizaje
Verifica que todos los componentes estén correctamente instalados
"""

import sys
import os

# Agregar la carpeta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("VALIDACIÓN DEL SISTEMA DE ÍNDICES DE APRENDIZAJE")
print("=" * 70)

# 1. Verificar que los archivos existen
print("\n✓ Verificando archivos...")
archivos_requeridos = {
    "Models": ["indice_aprendizaje.py", "evaluacion_indice.py"],
    "Controllers": ["indices_controller.py"],
    "Views/profesor": ["indices.html", "crear_indice.html", "evaluar_indice.html"],
    "Database": ["indices_aprendizaje.sql"]
}

todos_existen = True
for carpeta, archivos in archivos_requeridos.items():
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        if os.path.exists(ruta):
            print(f"  ✅ {ruta}")
        else:
            print(f"  ❌ FALTA: {ruta}")
            todos_existen = False

if not todos_existen:
    print("\n⚠️  Algunos archivos están faltando. Verifica la instalación.")
    sys.exit(1)

# 2. Verificar que los imports funcionan
print("\n✓ Verificando imports...")
try:
    from Models.indice_aprendizaje import IndiceAprendizaje
    print("  ✅ IndiceAprendizaje importado correctamente")
except ImportError as e:
    print(f"  ❌ Error importando IndiceAprendizaje: {e}")
    sys.exit(1)

try:
    from Models.evaluacion_indice import EvaluacionIndice
    print("  ✅ EvaluacionIndice importado correctamente")
except ImportError as e:
    print(f"  ❌ Error importando EvaluacionIndice: {e}")
    sys.exit(1)

try:
    from Controllers.indices_controller import IndicesController
    print("  ✅ IndicesController importado correctamente")
except ImportError as e:
    print(f"  ❌ Error importando IndicesController: {e}")
    sys.exit(1)

# 3. Verificar que las clases tienen los métodos necesarios
print("\n✓ Verificando métodos en modelos y controlador...")

metodos_requeridos = {
    "IndiceAprendizaje": [
        "crear_indice",
        "obtener_indices_por_materia",
        "obtener_indice_por_id",
        "actualizar_indice",
        "eliminar_indice",
        "contar_indices_por_materia"
    ],
    "EvaluacionIndice": [
        "crear_evaluacion",
        "obtener_ultima_evaluacion",
        "obtener_promedio_dominio"
    ],
    "IndicesController": [
        "crear_indice",
        "obtener_indices_por_materia",
        "obtener_indice_por_id",
        "guardar_evaluacion_indice",
        "eliminar_indice"
    ]
}

todas_present_methods = True
for clase_nombre, metodos in metodos_requeridos.items():
    if clase_nombre == "IndiceAprendizaje":
        clase = IndiceAprendizaje
    elif clase_nombre == "EvaluacionIndice":
        clase = EvaluacionIndice
    else:
        clase = IndicesController
    
    for metodo in metodos:
        if hasattr(clase, metodo):
            print(f"  ✅ {clase_nombre}.{metodo}()")
        else:
            print(f"  ❌ FALTA: {clase_nombre}.{metodo}()")
            todas_present_methods = False

if not todas_present_methods:
    print("\n⚠️  Algunos métodos están faltando.")
    sys.exit(1)

# 4. Verificar rutas en main.py
print("\n✓ Verificando rutas en main.py...")
try:
    with open("main.py", "r") as f:
        contenido = f.read()
    
    rutas_requeridas = [
        "@app.route('/profesor/indices'",
        "@app.route('/profesor/crear_indice'",
        "@app.route('/profesor/evaluar_indice'",
        "@app.route('/profesor/editar_indice'",
        "@app.route('/profesor/eliminar_indice'",
        "from Controllers.indices_controller import IndicesController"
    ]
    
    todas_rutas_present = True
    for ruta in rutas_requeridas:
        if ruta in contenido:
            print(f"  ✅ {ruta[:50]}...")
        else:
            print(f"  ❌ FALTA: {ruta[:50]}...")
            todas_rutas_present = False
    
    if not todas_rutas_present:
        print("\n⚠️  Algunas rutas no están configuradas en main.py")
        sys.exit(1)
        
except Exception as e:
    print(f"  ❌ Error verificando main.py: {e}")
    sys.exit(1)

# 5. Verificar vistas HTML
print("\n✓ Verificando contenido de vistas...")
vistas_a_verificar = {
    "Views/profesor/indices.html": [
        "Selecciona una materia",
        "url_for('crear_indice')",
        "url_for('evaluar_indice')"
    ],
    "Views/profesor/crear_indice.html": [
        "Nombre del Índice",
        "Porcentaje de Importancia",
        "Parcial"
    ],
    "Views/profesor/evaluar_indice.html": [
        "Porcentaje de Dominio",
        "Histórico de Evaluaciones",
        "Comentarios Adicionales"
    ]
}

todas_vistas_ok = True
for vista, elementos in vistas_a_verificar.items():
    try:
        with open(vista, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        for elemento in elementos:
            if elemento in contenido:
                print(f"  ✅ {vista.split('/')[-1]} contiene '{elemento[:30]}...'")
            else:
                print(f"  ❌ {vista.split('/')[-1]} NO CONTIENE '{elemento}'")
                todas_vistas_ok = False
    except Exception as e:
        print(f"  ❌ Error leyendo {vista}: {e}")
        todas_vistas_ok = False

if not todas_vistas_ok:
    print("\n⚠️  Algunas vistas están incompletas o mal configuradas.")
    sys.exit(1)

# 6. Resumen final
print("\n" + "=" * 70)
print("✅ VALIDACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 70)
print("""
El sistema de Índices de Aprendizaje está correctamente instalado.

PRÓXIMOS PASOS:
1. Ejecutar el script SQL: Database/indices_aprendizaje.sql
2. Reiniciar el servidor Flask
3. Acceder a /profesor/indices desde el navegador
4. Seleccionar una materia y comenzar a crear índices

DOCUMENTACIÓN:
Consulta INDICES_APRENDIZAJE_README.md para más información

SOPORTE:
Si encuentras errores, verifica la conexión a base de datos y que 
las tablas estén creadas con el script SQL.
""")
print("=" * 70)
