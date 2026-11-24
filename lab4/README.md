# PPOIS Lab 4 (variant 3) - Python 3.11+

Two required parts:
- `sorts.py`: generic `comb_sort()` and `tournament_sort()` for Python lists, including custom objects via `key`.
- `graph.py`: undirected *simple* graph using an incidence matrix (rows=vertices, columns=edges).

## Run

```bash
python main.py
```

All user input in the CLI is handled as strings for graph vertices. The algorithms themselves also support other value types.

## Tests / coverage

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q --cov=sorts --cov=graph --cov=main --cov-report=term-missing --cov-fail-under=91
```

## Documentation

```bash
pdoc ./graph.py ./sorts.py -o docs
```

## Graph API

```python
from graph import Graph

graph = Graph[str]()
for item in ("A", "B", "C"):
    graph.add_vertex(item)
graph.add_edge("A", "B")
graph.add_edge("B", "C")

print(graph.vertex_degree("B"))
print(graph.edge_degree("A", "B"))
print(list(graph.iter_vertices()))
print(list(graph.iter_edges()))
print(list(graph.iter_incident_edges("B")))
print(list(graph.iter_adjacent_vertices("B", reverse=True, const=True)))

iterator = graph.iter_vertices()
next(iterator)               # select first vertex
print(iterator.current)
print(iterator.prev())       # backward movement
# graph.remove_vertex_at(iterator)  # erases selected vertex

copy = graph.copy()
other = Graph()
other.assign_from(copy)
print(other == graph)
```

Rules:
- Vertex values must support equality (`==`). Unhashable values are supported.
- Duplicate vertices/edges and loops raise `ValueError`.
- Deleting a vertex also deletes its incident edges.
- `edge_degree(u,v)` counts other edges meeting this edge (line-graph degree).
- Comparisons use subgraph inclusion (`<=`, `>=`; strict versions `<`, `>`).
- A structural mutation invalidates existing iterators (`RuntimeError`).
- Iterator `prev()` walks backward in its chosen direction; `reverse=True` changes traversal direction.
- `const=True` returns deep-copied values and disallows erase through that iterator.
- `copy()` and `assign_from()` perform deep copying; no destructor is needed under Python's automatic memory management.

## Repository rules

Put this folder at repository root as `lab4/`, alongside `lab1/`, `lab2/`, `lab3/`.
Commit on a feature branch and open a PR. Do not merge without teacher approval.
