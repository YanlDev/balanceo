#!/usr/bin/env python3
"""
Test básico para verificar la funcionalidad del algoritmo RPW.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modelos.tarea import Tarea
from modelos.linea_produccion import LineaProduccion
from servicios.balanceador_rpw import BalanceadorRPW
from servicios.calculadora_metricas import CalculadoraMetricas


def test_algoritmo_rpw():
    """Test básico del algoritmo RPW con datos de ejemplo."""

    print("🧪 INICIANDO TEST DEL ALGORITMO RPW")
    print("=" * 50)

    try:
        # 1. Crear línea de producción
        print("1️⃣ Creando línea de producción...")
        linea = LineaProduccion(demanda_diaria=100, tiempo_disponible=480)  # 8 horas

        # 2. Crear tareas de ejemplo
        print("2️⃣ Agregando tareas de ejemplo...")

        # Tareas sin precedencias
        tarea_a = Tarea("A", "Preparar material", 5.0, [])
        tarea_b = Tarea("B", "Cortar piezas", 3.0, [])

        # Tareas con precedencias
        tarea_c = Tarea("C", "Ensamblar parte 1", 7.0, ["A"])
        tarea_d = Tarea("D", "Ensamblar parte 2", 4.0, ["B"])
        tarea_e = Tarea("E", "Soldar unión", 6.0, ["C", "D"])
        tarea_f = Tarea("F", "Pulir superficie", 2.0, ["E"])
        tarea_g = Tarea("G", "Pintar pieza", 8.0, ["F"])
        tarea_h = Tarea("H", "Empacar", 3.0, ["G"])

        # Agregar tareas a la línea
        for tarea in [tarea_a, tarea_b, tarea_c, tarea_d, tarea_e, tarea_f, tarea_g, tarea_h]:
            linea.agregar_tarea(tarea)

        print(f"   ✅ {len(linea.tareas)} tareas agregadas")

        # 3. Validar datos
        print("3️⃣ Validando precedencias y datos...")
        errores = linea.validar_precedencias()
        if errores:
            print(f"   ❌ Errores encontrados: {errores}")
            return False

        if linea.detectar_ciclos():
            print("   ❌ Ciclos detectados en precedencias")
            return False

        print("   ✅ Validación exitosa")

        # 4. Mostrar información básica
        print("4️⃣ Información de la línea:")
        tiempo_ciclo = linea.calcular_tiempo_ciclo()
        tiempo_total = linea.obtener_tiempo_total_tareas()
        min_estaciones = linea.calcular_numero_minimo_estaciones()

        print(f"   • Tiempo de ciclo: {tiempo_ciclo:.2f} min")
        print(f"   • Tiempo total tareas: {tiempo_total:.2f} min")
        print(f"   • Estaciones mínimas teóricas: {min_estaciones}")

        # 5. Ejecutar algoritmo RPW
        print("5️⃣ Ejecutando algoritmo RPW...")
        balanceador = BalanceadorRPW(linea)

        # Mostrar pesos posicionales calculados
        print("   📊 Pesos posicionales:")
        for tarea in linea.tareas.values():
            print(f"      {tarea.id}: {tarea.peso_posicional:.1f}")

        estaciones, estadisticas = balanceador.balancear()
        print(f"   ✅ Balanceamiento completado: {len(estaciones)} estaciones")

        # 6. Mostrar resultados
        print("6️⃣ Resultados del balanceamiento:")
        for estacion in estaciones:
            print(f"   {estacion}")
            print(f"      Utilización: {estacion.calcular_utilizacion():.1f}%")
            print(f"      Tiempo ocioso: {estacion.obtener_tiempo_ocioso():.2f} min")

        # 7. Calcular métricas completas
        print("7️⃣ Calculando métricas...")
        calculadora = CalculadoraMetricas(linea)
        metricas = calculadora.calcular_todas_las_metricas()

        eficiencia = metricas.get('metricas_eficiencia', {})
        print(f"   📈 Eficiencia de línea: {eficiencia.get('eficiencia_linea', 0):.1f}%")
        print(f"   ⚖️  Índice de suavidad: {eficiencia.get('indice_suavidad', 0):.2f}")

        # 8. Verificar coherencia
        print("8️⃣ Verificando coherencia de resultados...")

        # Verificar que todas las tareas están asignadas
        tareas_asignadas = set()
        for estacion in estaciones:
            tareas_asignadas.update(estacion.obtener_ids_tareas())

        if tareas_asignadas != set(linea.tareas.keys()):
            print("   ❌ No todas las tareas fueron asignadas")
            return False

        # Verificar que no hay sobrecargas de tiempo
        for estacion in estaciones:
            if estacion.tiempo_total > tiempo_ciclo + 0.01:  # Pequeña tolerancia
                print(f"   ❌ Estación {estacion.numero} excede tiempo de ciclo")
                return False

        print("   ✅ Verificación de coherencia exitosa")

        print("\n🎉 TEST COMPLETADO EXITOSAMENTE")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"❌ ERROR EN TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_casos_edge():
    """Test de casos extremos."""

    print("\n🔬 TESTING CASOS EXTREMOS")
    print("=" * 30)

    try:
        # Caso 1: Una sola tarea
        print("📝 Caso 1: Una sola tarea")
        linea1 = LineaProduccion(10, 60)
        linea1.agregar_tarea(Tarea("UNICA", "Tarea única", 3.0))

        balanceador1 = BalanceadorRPW(linea1)
        estaciones1, _ = balanceador1.balancear()

        if len(estaciones1) != 1:
            print("   ❌ Error en caso de tarea única")
            return False
        print("   ✅ Caso 1 exitoso")

        # Caso 2: Tareas secuenciales largas
        print("📝 Caso 2: Cadena secuencial")
        linea2 = LineaProduccion(20, 120)

        tarea_anterior = None
        for i in range(5):
            precedencias = [tarea_anterior.id] if tarea_anterior else []
            tarea = Tarea(f"SEQ{i+1}", f"Tarea secuencial {i+1}", 2.0, precedencias)
            linea2.agregar_tarea(tarea)
            tarea_anterior = tarea

        balanceador2 = BalanceadorRPW(linea2)
        estaciones2, _ = balanceador2.balancear()

        print(f"   ✅ Caso 2 exitoso: {len(estaciones2)} estaciones")

        print("🎯 Casos extremos completados exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error en casos extremos: {e}")
        return False


if __name__ == "__main__":
    print("CALCULADORA RPW - VERIFICACIÓN DE FUNCIONALIDAD")
    print("=" * 60)

    # Ejecutar tests
    test_principal = test_algoritmo_rpw()
    test_extremos = test_casos_edge()

    print("\n📋 RESUMEN DE TESTS:")
    print("=" * 30)
    print(f"Test principal: {'✅ EXITOSO' if test_principal else '❌ FALLIDO'}")
    print(f"Test casos extremos: {'✅ EXITOSO' if test_extremos else '❌ FALLIDO'}")

    if test_principal and test_extremos:
        print("\n🏆 TODOS LOS TESTS PASARON - EL SISTEMA ESTÁ FUNCIONANDO CORRECTAMENTE")
        exit_code = 0
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
        exit_code = 1

    input("\nPresione Enter para continuar...")
    sys.exit(exit_code)