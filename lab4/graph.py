
from copy import deepcopy
from typing import Generic, TypeVar

T = TypeVar("T")


class GraphIterator(Generic[T]):
    def __init__(self, graph, kind, entries, reverse=False, const=False):
        self._graph = graph
        self._kind = kind
        self._entries = list(reversed(entries)) if reverse else list(entries)
        self._const = const
        self._version = graph._version
        self._position = 0
        self._selected = None
        self._has_selected = False

    def _check(self):
        if self._version != self._graph._version:
            raise RuntimeError("Iterator invalidated by graph modification")

    def _view(self, item):
        return deepcopy(item) if self._const else item

    def __iter__(self):
        return self

    def __next__(self):
        self._check()
        if self._position >= len(self._entries):
            raise StopIteration
        self._selected = self._entries[self._position]
        self._has_selected = True
        self._position += 1
        return self._view(self._selected)

    def prev(self):
        self._check()
        if self._position == 0:
            raise StopIteration
        self._position -= 1
        self._selected = self._entries[self._position]
        self._has_selected = True
        return self._view(self._selected)

    @property
    def current(self):
        self._check()
        if not self._has_selected:
            raise ValueError("Iterator has not selected an element")
        return self._view(self._selected)


class Graph(Generic[T]):
    def __init__(self):
        self._vertices: list[T] = []
        self._matrix: list[list[int]] = []
        self._edge_count = 0
        self._version = 0

    def _vertex_index(self, value):
        for index, vertex in enumerate(self._vertices):
            if vertex == value:
                return index
        raise ValueError("Vertex does not exist")

    def _edge_columns(self, first_index, second_index):
        for column in range(self._edge_count):
            if self._matrix[first_index][column] and self._matrix[second_index][column]:
                yield column

    def _edge_column(self, first, second):
        first_index = self._vertex_index(first)
        second_index = self._vertex_index(second)
        for column in self._edge_columns(first_index, second_index):
            return column
        raise ValueError("Edge does not exist")

    def _edge_pairs(self):
        pairs = []
        for column in range(self._edge_count):
            endpoints = [index for index, row in enumerate(self._matrix) if row[column]]
            pairs.append((self._vertices[endpoints[0]], self._vertices[endpoints[1]]))
        return pairs

    def is_empty(self):
        return not self._vertices

    def clear(self):
        self._vertices.clear()
        self._matrix.clear()
        self._edge_count = 0
        self._version += 1

    def vertex_count(self):
        return len(self._vertices)

    def edge_count(self):
        return self._edge_count

    def has_vertex(self, value):
        return any(vertex == value for vertex in self._vertices)

    def has_edge(self, first, second):
        if first == second or not self.has_vertex(first) or not self.has_vertex(second):
            return False
        return next(self._edge_columns(self._vertex_index(first), self._vertex_index(second)), None) is not None

    def add_vertex(self, value):
        if self.has_vertex(value):
            raise ValueError("Vertex already exists")
        self._vertices.append(value)
        self._matrix.append([0] * self._edge_count)
        self._version += 1

    def add_edge(self, first, second):
        first_index = self._vertex_index(first)
        second_index = self._vertex_index(second)
        if first_index == second_index:
            raise ValueError("Loops are not supported")
        if self.has_edge(first, second):
            raise ValueError("Edge already exists")
        for row in self._matrix:
            row.append(0)
        self._matrix[first_index][-1] = 1
        self._matrix[second_index][-1] = 1
        self._edge_count += 1
        self._version += 1

    def _remove_column(self, column):
        for row in self._matrix:
            row.pop(column)
        self._edge_count -= 1

    def remove_edge(self, first, second):
        column = self._edge_column(first, second)
        self._remove_column(column)
        self._version += 1

    def remove_vertex(self, value):
        index = self._vertex_index(value)
        columns = [column for column, present in enumerate(self._matrix[index]) if present]
        for column in reversed(columns):
            self._remove_column(column)
        self._matrix.pop(index)
        self._vertices.pop(index)
        self._version += 1

    def vertex_degree(self, value):
        return sum(self._matrix[self._vertex_index(value)])

    def edge_degree(self, first, second):
        self._edge_column(first, second)
        return self.vertex_degree(first) + self.vertex_degree(second) - 2

    def get_vertex(self, value):
        return deepcopy(self._vertices[self._vertex_index(value)])

    def iter_vertices(self, reverse=False, const=False):
        return GraphIterator(self, "vertices", self._vertices, reverse, const)

    def iter_edges(self, reverse=False, const=False):
        return GraphIterator(self, "edges", self._edge_pairs(), reverse, const)

    def iter_incident_edges(self, value, reverse=False, const=False):
        index = self._vertex_index(value)
        edges = [pair for column, pair in enumerate(self._edge_pairs()) if self._matrix[index][column]]
        return GraphIterator(self, "edges", edges, reverse, const)

    def iter_adjacent_vertices(self, value, reverse=False, const=False):
        index = self._vertex_index(value)
        neighbors = []
        for column in range(self._edge_count):
            if self._matrix[index][column]:
                other = next(row for row in range(self.vertex_count())
                             if row != index and self._matrix[row][column])
                neighbors.append(self._vertices[other])
        return GraphIterator(self, "adjacent", neighbors, reverse, const)

    def _check_iterator(self, iterator, expected_kind):
        if not isinstance(iterator, GraphIterator) or iterator._graph is not self:
            raise ValueError("Iterator belongs to another graph")
        iterator._check()
        if iterator._kind != expected_kind:
            raise ValueError("Wrong iterator type")
        if iterator._const:
            raise ValueError("Cannot erase through a read-only iterator")
        if not iterator._has_selected:
            raise ValueError("Iterator has not selected an element")

    def remove_vertex_at(self, iterator):
        self._check_iterator(iterator, "vertices")
        self.remove_vertex(iterator._selected)

    def remove_edge_at(self, iterator):
        self._check_iterator(iterator, "edges")
        first, second = iterator._selected
        self.remove_edge(first, second)

    def copy(self):
        """Deep-copy graph, including mutable vertex values."""
        duplicate = Graph()
        duplicate._vertices = deepcopy(self._vertices)
        duplicate._matrix = deepcopy(self._matrix)
        duplicate._edge_count = self._edge_count
        return duplicate

    def assign_from(self, other):
        if not isinstance(other, Graph):
            raise TypeError("Expected a Graph")
        if other is self:
            return self
        new_vertices = deepcopy(other._vertices)
        new_matrix = deepcopy(other._matrix)
        self._vertices = new_vertices
        self._matrix = new_matrix
        self._edge_count = other._edge_count
        self._version += 1
        return self

    def __iter__(self):
        return self.iter_vertices()

    def __reversed__(self):
        return self.iter_vertices(reverse=True)

    def __str__(self):
        vertices = list(self.iter_vertices(const=True))
        edges = list(self.iter_edges(const=True))
        return f"Graph(vertices={vertices}, edges={edges})"

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return (self.vertex_count() == other.vertex_count()
                and self.edge_count() == other.edge_count()
                and self <= other)

    def __ne__(self, other):
        result = self.__eq__(other)
        return NotImplemented if result is NotImplemented else not result

    def __le__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return (all(other.has_vertex(v) for v in self.iter_vertices())
                and all(other.has_edge(a, b) for a, b in self.iter_edges()))

    def __lt__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return self <= other and self != other

    def __ge__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return other <= self

    def __gt__(self, other):
        if not isinstance(other, Graph):
            return NotImplemented
        return self >= other and self != other
