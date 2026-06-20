# ==============================================================================
#                                  MAKEFILE
# ==============================================================================

# Variables de entorno y ejecutables
VENV     = .venv
PYTHON   = $(VENV)/bin/python3
PIP      = $(VENV)/bin/pip3
MAIN     = fly-in.py
SRC_DIR  = .

# Regla por defecto (ejecuta el linter y luego el simulador)
all: install lint run

# 1. Instalar dependencias del entorno académicas
install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	@echo "Creando entorno virtual aislado ($(VENV))..."
	python3 -m venv $(VENV)
	@echo "Actualizando pip e instalando dependencias (pygame, flake8, mypy)..."
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy pygame
	@touch $(VENV)/bin/activate

# 2. Ejecutar el script principal del simulador
run:
	@echo "Iniciando la simulación gráfica de Fly-in con Pygame..."
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

fclean: clean
	@echo "Eliminando entorno virtual..."
	rm -rf $(VENV)

# 5. Verificación estricta de linter y tipado estático
lint:
	@echo "== [1/2] Verificando estilo con Flake8 =="
	$(VENV)/bin/flake8 $(SRC_DIR) --max-line-length=79 --exclude=$(VENV)
	@echo "== [2/2] Verificando tipado estricto con Mypy =="
	$(VENV)/bin/mypy $(SRC_DIR) --disallow-untyped-defs --ignore-missing-imports --exclude $(VENV)

re: fclean all

.PHONY: all install run debug clean fclean lint re