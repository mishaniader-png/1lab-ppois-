"""Graph API, iterators, copying, comparisons, and invalidation tests."""

from dataclasses import dataclass

import pytest

from graph import Graph


@pytest.fixture
def graph():
    result = Graph()
    for name in ("A", "B", "C", "D"):
        result.add_vertex(name)
    result.add_edge("A", "B")
    result.add_edge("A", "C")
    result.add_edge("B", "C")
    return result


def test_empty_new_graph_and_str():
    graph = Graph[int]()
    assert graph.is_empty()
    assert graph.vertex_count() == graph.edge_count() == 0
    assert str(graph) == "Graph(vertices=[], edges=[])"
    assert list(graph) == []
    assert list(reversed(graph)) == []
    assert list(graph.iter_edges()) == []


def test_counts_membership_and_degrees(graph):
    assert not graph.is_empty()
    assert graph.vertex_count() == 4
    assert graph.edge_count() == 3
    assert graph.has_vertex("A")
    assert not graph.has_vertex("Q")
    assert graph.has_edge("B", "A")
    assert not graph.has_edge("A", "D")
    assert not graph.has_edge("Q", "C")
    assert not graph.has_edge("A", "A")
    assert graph.vertex_degree("A") == 2
    assert graph.vertex_degree("D") == 0
    assert graph.edge_degree("A", "B") == 2


def test_invalid_add_and_query(graph):
    with pytest.raises(ValueError, match="already exists"):
        graph.add_vertex("A")
    with pytest.raises(ValueError, match="does not exist"):
        graph.add_edge("A", "Q")
    with pytest.raises(ValueError, match="Loops"):
        graph.add_edge("A", "A")
    with pytest.raises(ValueError, match="already exists"):
        graph.add_edge("B", "A")
    with pytest.raises(ValueError, match="does not exist"):
        graph.vertex_degree("Q")
    with pytest.raises(ValueError, match="does not exist"):
        graph.edge_degree("A", "D")
    with pytest.raises(ValueError, match="does not exist"):
        graph.get_vertex("Q")


def test_remove_edge_and_vertex(graph):
    graph.remove_edge("C", "B")
    assert graph.edge_count() == 2
    assert not graph.has_edge("B", "C")
    with pytest.raises(ValueError, match="Edge does not exist"):
        graph.remove_edge("B", "C")
    graph.remove_vertex("A")
    assert graph.vertex_count() == 3
    assert graph.edge_count() == 0
    assert list(graph.iter_vertices()) == ["B", "C", "D"]
    with pytest.raises(ValueError, match="Vertex does not exist"):
        graph.remove_vertex("A")
    graph.clear()
    assert graph.is_empty()
    assert graph.edge_count() == 0
    graph.clear()


def test_iterators_all_four_types(graph):
    assert list(graph.iter_vertices()) == ["A", "B", "C", "D"]
    assert list(graph.iter_edges()) == [("A", "B"), ("A", "C"), ("B", "C")]
    assert list(graph.iter_incident_edges("A")) == [("A", "B"), ("A", "C")]
    assert list(graph.iter_adjacent_vertices("A")) == ["B", "C"]
    assert list(graph.iter_incident_edges("D")) == []
    assert list(graph.iter_adjacent_vertices("D")) == []
    assert list(graph.iter_vertices(reverse=True)) == ["D", "C", "B", "A"]
    assert list(reversed(graph)) == ["D", "C", "B", "A"]
    assert list(graph.iter_edges(reverse=True)) == [("B", "C"), ("A", "C"), ("A", "B")]
    assert list(graph.iter_incident_edges("A", reverse=True)) == [("A", "C"), ("A", "B")]
    assert list(graph.iter_adjacent_vertices("A", reverse=True)) == ["C", "B"]
    assert list(graph.iter_vertices(const=True)) == ["A", "B", "C", "D"]
    assert list(graph.iter_edges(const=True)) == [("A", "B"), ("A", "C"), ("B", "C")]
    assert list(graph.iter_incident_edges("A", const=True)) == [("A", "B"), ("A", "C")]
    assert list(graph.iter_adjacent_vertices("A", const=True)) == ["B", "C"]
    assert "edges=[('A', 'B')" in str(graph)


def test_iterator_backwards_and_current(graph):
    it = graph.iter_vertices()
    assert iter(it) is it
    with pytest.raises(ValueError, match="has not selected"):
        _ = it.current
    with pytest.raises(StopIteration):
        it.prev()
    assert next(it) == "A"
    assert it.current == "A"
    assert next(it) == "B"
    assert it.prev() == "B"
    assert next(it) == "B"
    assert next(it) == "C"
    assert next(it) == "D"
    with pytest.raises(StopIteration):
        next(it)
    assert it.prev() == "D"
    reverse = graph.iter_vertices(reverse=True)
    assert next(reverse) == "D"
    assert next(reverse) == "C"
    assert reverse.prev() == "C"


def test_invalidation(graph):
    iterator = graph.iter_edges()
    next(iterator)
    graph.add_vertex("E")
    with pytest.raises(RuntimeError, match="invalidated"):
        next(iterator)
    with pytest.raises(RuntimeError, match="invalidated"):
        iterator.prev()
    with pytest.raises(RuntimeError, match="invalidated"):
        _ = iterator.current


def test_erase_by_iterator(graph):
    vertices = graph.iter_vertices()
    next(vertices)
    graph.remove_vertex_at(vertices)
    assert not graph.has_vertex("A")
    assert graph.vertex_count() == 3
    assert graph.edge_count() == 1
    edges = graph.iter_edges()
    assert next(edges) == ("B", "C")
    graph.remove_edge_at(edges)
    assert graph.edge_count() == 0


def test_erase_iterator_errors(graph):
    graph2 = graph.copy()
    iterator = graph.iter_vertices()
    with pytest.raises(ValueError, match="has not selected"):
        graph.remove_vertex_at(iterator)
    next(iterator)
    with pytest.raises(ValueError, match="another graph"):
        graph2.remove_vertex_at(iterator)
    with pytest.raises(ValueError, match="another graph"):
        graph.remove_vertex_at("not an iterator")
    with pytest.raises(ValueError, match="Wrong iterator"):
        graph.remove_edge_at(iterator)
    const_it = graph.iter_vertices(const=True)
    next(const_it)
    with pytest.raises(ValueError, match="read-only"):
        graph.remove_vertex_at(const_it)
    graph.remove_edge("A", "B")
    with pytest.raises(RuntimeError, match="invalidated"):
        graph.remove_vertex_at(iterator)


def test_copy_assign_and_independence(graph):
    clone = graph.copy()
    assert clone == graph
    assert clone is not graph
    clone.add_vertex("E")
    assert clone != graph
    assert not graph.has_vertex("E")
    other = Graph()
    assert other.assign_from(graph) is other
    assert other == graph
    assert other.assign_from(other) is other
    with pytest.raises(TypeError, match="Expected a Graph"):
        other.assign_from([1])


def test_comparisons(graph):
    identical = Graph()
    for name in ("D", "C", "B", "A"):
        identical.add_vertex(name)
    for first, second in (("C", "B"), ("C", "A"), ("B", "A")):
        identical.add_edge(first, second)
    assert identical == graph
    assert not identical != graph
    assert identical <= graph
    assert identical >= graph
    assert not identical < graph
    assert not identical > graph
    small = Graph()
    small.add_vertex("A")
    small.add_vertex("B")
    small.add_edge("A", "B")
    assert small < graph
    assert small <= graph
    assert graph > small
    assert graph >= small
    assert not graph <= small
    assert not graph < small
    assert not small > graph
    assert not small >= graph
    unrelated = Graph()
    unrelated.add_vertex("Z")
    assert not unrelated <= graph
    assert not graph <= unrelated
    assert graph != unrelated


def test_compare_non_graph(graph):
    assert graph != "something else"
    for operator in (
        lambda x: x < "string", lambda x: x <= "string",
        lambda x: x > "string", lambda x: x >= "string"
    ):
        with pytest.raises(TypeError):
            operator(graph)


@dataclass
class MutableVertex:
    name: str
    tags: list[str]


def test_mutable_unhashable_vertices_and_deep_copy():
    graph = Graph()
    a = MutableVertex("A", ["original"])
    b = MutableVertex("B", ["other"])
    graph.add_vertex(a)
    graph.add_vertex(b)
    graph.add_edge(a, b)
    duplicate = graph.copy()
    copied = duplicate.get_vertex(a)
    copied.tags.append("changed")
    assert graph.get_vertex(a).tags == ["original"]
    assert duplicate.get_vertex(a).tags == ["original"]
    const_it = graph.iter_vertices(const=True)
    shown = next(const_it)
    shown.tags.append("changed")
    assert graph.get_vertex(a).tags == ["original"]
    assigned = Graph()
    assigned.assign_from(graph)
    a.tags.append("mutated")
    assert assigned.get_vertex(MutableVertex("A", ["original"])).tags == ["original"]


def test_bad_iterators(graph):
    with pytest.raises(ValueError, match="does not exist"):
        list(graph.iter_incident_edges("Q"))
    with pytest.raises(ValueError, match="does not exist"):
        list(graph.iter_adjacent_vertices("Q"))
