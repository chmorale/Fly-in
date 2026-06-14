# ==============================================================================
#                                  MAKEFILE
# ==============================================================================

# Variables de entorno y ejecutables
PYTHON   = python3
PIP      = pip3
MAIN     = fly-in.py
SRC_DIR  = .

# Regla por defecto (ejecuta el linter y luego el simulador)
all: lint run

# 1. Instalar dependencias del entorno académicas
install:
	@echo "Instalando herramientas de desarrollo y tipado..."
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

# 2. Ejecutar el script principal del simulador
run:
	@echo "Iniciando la simulación de Fly-in..."
	$(PYTHON) $(MAIN)

# 3. Ejecutar en modo depuración interactiva (pdb)
debug:
	@echo "Iniciando depurador interactivo (PDB)..."
	$(PYTHON) -m pdb $(MAIN)

# 4. Limpieza absoluta de residuos de caché y temporales
clean:
	@echo "Limpiando archivos temporales y cachés de Python..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache

# 5. Verificación estricta de linter y tipado estático
lint:
	@echo "== [1/2] Verificando estilo con Flake8 =="
	flake8 $(SRC_DIR) --max-line-length=79
	@echo "== [2/2] Verificando tipado estricto con Mypy =="
	mypy $(SRC_DIR) --disallow-untyped-defs --ignore-missing-imports

.PHONY: all install run debug clean lint
