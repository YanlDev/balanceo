# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Production Line Balancing Calculator** using the **Ranked Positional Weight (RPW) algorithm**. It's a desktop GUI application built in Python with Tkinter that helps optimize manufacturing line efficiency by balancing workstation assignments.

## Architecture

### Core Components

- **Domain Models** (`modelos/`): Core business entities
  - `Tarea`: Represents production tasks with dependencies and timing
  - `Estacion`: Workstation that can hold multiple tasks within cycle time limits
  - `LineaProduccion`: Complete production line managing tasks and stations

- **Services** (`servicios/`): Business logic implementation
  - `BalanceadorRPW`: Implements the RPW algorithm for line balancing
  - `CalculadoraMetricas`: Computes efficiency metrics and statistics

- **UI Components** (`ui/`): Tkinter-based interface
  - `VentanaPrincipal`: Main application window coordinating all components
  - `ui/componentes/`: Modular UI panels (input, results, charts)

- **Utilities** (`utils/`): Cross-cutting concerns
  - `estilos.py`: Modern UI styling and theming
  - `validacion.py`: Input validation and error handling

### Key Algorithms

**RPW (Ranked Positional Weight)** algorithm implementation:
1. Calculate positional weights for all tasks (task time + sum of successor times)
2. Sort tasks by weight (descending)
3. Assign tasks to stations sequentially, respecting precedence constraints
4. Create new station if task doesn't fit in existing ones

### Data Flow

1. User inputs tasks (ID, description, time, precedences) and line config (demand, available time)
2. `LineaProduccion` validates precedences and detects cycles
3. `BalanceadorRPW` executes algorithm and returns balanced stations
4. `CalculadoraMetricas` computes efficiency metrics
5. UI updates with results, charts, and statistics

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run main application
python ui/ventana_principal.py
```

### Dependencies
- `matplotlib>=3.6.0` - Charts and visualization
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computations

## Code Conventions

- **Language**: Spanish variable names and comments (business domain requirement)
- **Type Hints**: Used throughout for better code documentation
- **Error Handling**: Custom `ValidacionError` exceptions for business logic errors
- **UI Architecture**: Component-based with separation of concerns
- **Data Validation**: Input validation at multiple layers (UI, domain models)

## Key Files to Understand

- `servicios/balanceador_rpw.py:24-49` - Main algorithm implementation
- `modelos/linea_produccion.py:90-118` - Precedence cycle detection
- `ui/ventana_principal.py:248-330` - Application orchestration and async execution
- `modelos/tarea.py:50-64` - Positional weight calculation

## Common Tasks

- **Adding new validation rules**: Extend `utils/validacion.py`
- **Modifying RPW algorithm**: Work in `servicios/balanceador_rpw.py`
- **UI styling changes**: Update `utils/estilos.py`
- **New metrics**: Extend `servicios/calculadora_metricas.py`