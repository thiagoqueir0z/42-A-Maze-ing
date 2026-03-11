# A-Maze-ing

Projeto de geração e visualização de labirinto em Python + MLX.

## Executar

```bash
make run
```

ou

```bash
python3 a_maze_ing.py config.txt
```

## Dependências

- Python 3
- MLX (uma das opções abaixo)

### Opção 1 — MLX local no projeto

Use a biblioteca local em `mazegen/mlx/libmlx.so`.

```bash
python3 a_maze_ing.py config.txt
```

### Opção 2 — MLX instalada pelo avaliador

Sem `libmlx.so` local, o projeto usa a MLX instalada no sistema do avaliador.

Você pode apontar explicitamente com `MLX_SO_PATH`:

```bash
export MLX_SO_PATH=/usr/lib/libmlx.so
python3 a_maze_ing.py config.txt
```

### Ordem de carregamento da MLX

O wrapper tenta, nesta ordem:

1. `MLX_SO_PATH` (variável de ambiente)
2. `mazegen/mlx/libmlx.so` (arquivo local)
3. biblioteca do sistema (`libmlx.so` / `mlx`)

## Entrega (recomendado)

- Não enviar `venv/`
- Não enviar wheels locais (`*.whl`)
- Não enviar saídas geradas (`maze.txt`)

## Qualidade (opcional)

```bash
make install
make lint
```

## Reusable Module: mazegen

This project includes a reusable maze generation package.

### Installation
```bash
pip install ./mazegen_mariaalm-1.0.0-py3-none-any.whl