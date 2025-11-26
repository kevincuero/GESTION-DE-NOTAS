#!/bin/bash
# setup_notificaciones.sh - Script de instalación del sistema de notificaciones

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       INSTALACIÓN - SISTEMA DE NOTIFICACIONES              ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "PASO 1: Verificando estructura de archivos..."
echo "================================================"

# Verificar archivos críticos
archivos=(
    "Models/notificacion.py"
    "Controllers/notificacion_controller.py"
    "Views/profesor/EnviarNotificacion.html"
    "Views/estudiante/mis_notificaciones.html"
    "Database/actualizar_notificaciones.sql"
    "test_notificaciones.py"
)

for archivo in "${archivos[@]}"; do
    if [ -f "$archivo" ]; then
        echo "✅ $archivo"
    else
        echo "❌ FALTA: $archivo"
        exit 1
    fi
done

echo ""
echo "PASO 2: Verificando que el servidor NO esté corriendo..."
echo "==========================================================="

if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  El servidor Flask está corriendo"
    read -p "¿Detener servidor? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        pkill -f "python.*main.py"
        echo "✅ Servidor detenido"
    fi
fi

echo ""
echo "PASO 3: Instalando dependencias de Python..."
echo "============================================="

pip install -q flask mysql-connector-python pymysql werkzeug authlib
echo "✅ Dependencias instaladas"

echo ""
echo "PASO 4: Información de Base de Datos"
echo "===================================="

read -p "Host MySQL (default: localhost): " host
host=${host:-localhost}

read -p "Usuario MySQL (default: root): " usuario
usuario=${usuario:-root}

read -s -p "Contraseña MySQL: " password
echo ""

read -p "Base de datos (default: GestionDeEstudiantes): " bd
bd=${bd:-GestionDeEstudiantes}

echo ""
echo "PASO 5: Ejecutando migración de BD..."
echo "======================================"

mysql -h "$host" -u "$usuario" -p"$password" < Database/actualizar_notificaciones.sql 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Base de datos actualizada"
else
    echo "⚠️  Revisar credenciales y ejecutar manualmente:"
    echo "   mysql -u $usuario -p < Database/actualizar_notificaciones.sql"
fi

echo ""
echo "PASO 6: Ejecutando tests..."
echo "============================"

python test_notificaciones.py

echo ""
echo "PASO 7: Iniciando servidor..."
echo "==============================="

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE           ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "PRÓXIMOS PASOS:"
echo "=============="
echo ""
echo "1. Iniciar servidor Flask:"
echo "   python main.py"
echo ""
echo "2. Acceder a:"
echo "   - Profesor: http://localhost:5000/profesor/enviar_notificacion"
echo "   - Estudiante: http://localhost:5000/estudiante/notificaciones"
echo ""
echo "3. Usar las credenciales de prueba:"
echo "   - Profesor: carlos@example.com / contraseña_encriptada"
echo "   - Estudiante: juan.delgado@example.com / contraseña_encriptada"
echo ""
echo "Para más información, revisar: README_NOTIFICACIONES.md"
echo ""
