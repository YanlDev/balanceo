#!/usr/bin/env python3
"""
Calculadora de Balanceamiento de Líneas - Algoritmo RPW
=======================================================

Aplicación de escritorio para el balanceamiento de líneas de producción
utilizando el algoritmo Ranked Positional Weight (RPW).

Autor: Sistema de Balanceamiento RPW
Versión: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar componentes principales
    from ui.ventana_principal import VentanaPrincipal
    from utils.validacion import ValidacionError

except ImportError as e:
    print(f"Error al importar módulos necesarios: {e}")
    print("Asegúrese de que todas las dependencias estén instaladas:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def verificar_dependencias():
    """Verifica que las dependencias necesarias estén instaladas."""
    dependencias_faltantes = []

    try:
        import matplotlib
    except ImportError:
        dependencias_faltantes.append("matplotlib")

    try:
        import pandas
    except ImportError:
        dependencias_faltantes.append("pandas")

    try:
        import numpy
    except ImportError:
        dependencias_faltantes.append("numpy")

    if dependencias_faltantes:
        mensaje = "Dependencias faltantes:\n\n"
        mensaje += "\n".join(f"• {dep}" for dep in dependencias_faltantes)
        mensaje += "\n\nInstale las dependencias con:\npip install -r requirements.txt"

        # Mostrar error en GUI si es posible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dependencias Faltantes", mensaje)
            root.destroy()
        except:
            print(mensaje)

        return False

    return True


def configurar_aplicacion():
    """Configura la aplicación antes de ejecutar."""
    # Configurar título de la ventana de consola en Windows
    try:
        if sys.platform.startswith('win'):
            os.system('title Calculadora RPW - Balanceamiento de Líneas')
    except:
        pass

    # Configurar ruta de trabajo
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Función principal de la aplicación."""
    print("=" * 60)
    print("CALCULADORA DE BALANCEAMIENTO DE LÍNEAS - ALGORITMO RPW")
    print("=" * 60)
    print("Iniciando aplicación...")

    # Configurar aplicación
    configurar_aplicacion()

    # Verificar dependencias
    print("Verificando dependencias...")
    if not verificar_dependencias():
        print("❌ Error: Dependencias faltantes. Vea el mensaje anterior.")
        input("Presione Enter para salir...")
        return 1

    print("✅ Dependencias verificadas correctamente.")

    # Inicializar y ejecutar aplicación
    try:
        print("🚀 Iniciando interfaz gráfica...")
        app = VentanaPrincipal()

        print("✅ Aplicación iniciada exitosamente.")
        print("💡 Cierre esta ventana de consola para terminar la aplicación.")
        print("=" * 60)

        # Ejecutar aplicación
        app.ejecutar()

        print("\n📋 Aplicación cerrada correctamente.")
        return 0

    except Exception as e:
        error_msg = f"Error crítico al iniciar la aplicación: {str(e)}"
        print(f"❌ {error_msg}")

        # Mostrar error en GUI si es posible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error Crítico", error_msg)
            root.destroy()
        except:
            pass

        print("\n🔧 Sugerencias para resolver el problema:")
        print("1. Reinstale las dependencias: pip install -r requirements.txt")
        print("2. Verifique que Python esté actualizado (3.7+)")
        print("3. Ejecute desde el directorio correcto del proyecto")

        input("\nPresione Enter para salir...")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Aplicación interrumpida por el usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)