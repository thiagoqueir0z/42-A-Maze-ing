PACKAGE  = a_maze_ing
NAME     = a_maze_ing.py
SRC      = a_maze_ing.py mazegen/
PYTHON   = python3
PIP      = pip
CONFIG   = config.txt


all: run

install:
	$(PYTHON) -m $(PIP) install --user flake8 mypy

run:
	$(PYTHON) $(NAME) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(NAME)

lint:
	$(PYTHON) -m flake8 $(SRC)
	$(PYTHON) -m mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy --strict .

clean:
	rm -rf dist/ build/ *.egg-info
	# rm -rf *.tar.gz *.whl
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) \
		-exec rm -rf {} + 2>/dev/null; true
	rm -f maze.txt

venv-clean:
	@echo "Removing common virtualenv directories..."
	@rm -rf .venv venv env .env .venv_build .venv_test .venv_test_sdist || true
	@echo "Searching for any directory containing pyvenv.cfg and removing it..."
	@# Procura por pyvenv.cfg até uma profundidade razoável e remove o diretório pai
	@find . -maxdepth 4 -type f -name "pyvenv.cfg" -print0 2>/dev/null \
		| xargs -0 -I{} sh -c 'd="$$(dirname "{}")"; echo "rm -rf $$d"; rm -rf "$$d"' || true
	@echo "Done."

.PHONY: all install run debug lint lint-strict clean venv-clean
