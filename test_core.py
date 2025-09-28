#!/usr/bin/env python3
"""
Test básico para verificar la funcionalidad core del algoritmo RPW (sin GUI).
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modelos.tarea import Tarea
from modelos.linea_produccion import LineaProduccion
from servicios.balanceador_rpw import BalanceadorRPW


def test_core_rpw():
    """Test del núcleo del algoritmo RPW."""

    print("🧪 TEST CORE DEL ALGORITMO RPW")
    print("=" * 40)

    try:
        # 1. Crear línea de producción
        print("1️⃣ Creando línea de producción...")
        linea = LineaProduccion(demanda_diaria=100, tiempo_disponible=480)

        # 2. Crear tareas simples
        print("2️⃣ Agregando tareas...")
        tareas_data = [
            ("A", "Tarea A", 5.0, []),
            ("B", "Tarea B", 3.0, []),
            ("C", "Tarea C", 7.0, ["A"]),
            ("D", "Tarea D", 4.0, ["B"]),
            ("E", "Tarea E", 6.0, ["C", "D"]),
        ]

        for id_tarea, desc, tiempo, precedencias in tareas_data:
            tarea = Tarea(id_tarea, desc, tiempo, precedencias)
            linea.agregar_tarea(tarea)

        print(f"   ✅ {len(linea.tareas)} tareas agregadas")

        # 3. Validar
        print("3️⃣ Validando...")
        errores = linea.validar_precedencias()
        if errores:
            print(f"   ❌ Errores: {errores}")
            return False

        if linea.detectar_ciclos():
            print("   ❌ Ciclos detectados")
            return False

        print("   ✅ Validación exitosa")

        # 4. Información básica
        print("4️⃣ Información básica:")
        tiempo_ciclo = linea.calcular_tiempo_ciclo()
        tiempo_total = linea.obtener_tiempo_total_tareas()
        min_estaciones = linea.calcular_numero_minimo_estaciones()

        print(f"   • Tiempo ciclo: {tiempo_ciclo:.2f} min")
        print(f"   • Tiempo total: {tiempo_total:.2f} min")
        print(f"   • Estaciones mín: {min_estaciones}")

        # 5. Ejecutar RPW
        print("5️⃣ Ejecutando RPW...")
        balanceador = BalanceadorRPW(linea)
        estaciones, estadisticas = balanceador.balancear()

        print(f"   ✅ {len(estaciones)} estaciones creadas")

        # 6. Mostrar resultados
        print("6️⃣ Resultados:")
        for estacion in estaciones:
            tareas = ", ".join(estacion.obtener_ids_tareas())
            print(f"   Estación {estacion.numero}: [{tareas}] "
                  f"({estacion.tiempo_total:.1f}min, "
                  f"{estacion.calcular_utilizacion():.1f}%)")

        # 7. Verificaciones
        print("7️⃣ Verificando...")

        # Todas las tareas asignadas
        tareas_asignadas = set()
        for estacion in estaciones:
            tareas_asignadas.update(estacion.obtener_ids_tareas())

        if tareas_asignadas != set(linea.tareas.keys()):
            print("   ❌ Tareas faltantes")
            return False

        # Sin sobrecarga de tiempo
        for estacion in estaciones:
            if estacion.tiempo_total > tiempo_ciclo + 0.01:
                print(f"   ❌ Estación {estacion.numero} sobrecargada")
                return False

        print("   ✅ Verificaciones exitosas")

        print("\n🎉 TEST CORE EXITOSO")
        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("VERIFICACIÓN CORE DEL ALGORITMO RPW")
    print("=" * 50)

    resultado = test_core_rpw()

    print("\n📋 RESULTADO:")
    if resultado:
        print("✅ ALGORITMO RPW FUNCIONANDO CORRECTAMENTE")
        exit_code = 0
    else:
        print("❌ ALGORITMO RPW TIENE PROBLEMAS")
        exit_code = 1

    sys.exit(exit_code)