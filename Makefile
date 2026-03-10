PACKAGE  = a_maze_ing
NAME     = a_maze_ing.py
SRC      = a_maze_ing.py mazegen/
PYTHON   = python3
PIP      = pip
CONFIG   = config.txt


all: run

install:
	$(PYTHON) -m $(PIP) install --user flake8 mypy
	$(PYTHON) -m $(PIP) install --user mlx-python || true

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
	rm -rf *.tar.gz *.whl
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) \
		-exec rm -rf {} + 2>/dev/null; true

.PHONY: all install run debug lint lint-strict clean
