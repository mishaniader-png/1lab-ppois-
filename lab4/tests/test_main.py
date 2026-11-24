"""Console flows are exercised without launching a real terminal."""

from unittest.mock import patch

import pytest

from graph import Graph
from main import graph_menu, main, next_selected, read_int, show_iterators, show_sorting


def inputs(*answers):
    return patch("builtins.input", side_effect=list(answers))


@pytest.mark.parametrize("algorithm,data_type,data", [
    ("1", "1", "5 2 1"), ("2", "1", "5 2 1"),
    ("1", "2", "pear apple"), ("2", "2", "pear apple"),
    ("1", "3", None), ("2", "3", None),
])
def test_sort_menu(algorithm, data_type, data, capsys):
    answers = [algorithm, data_type]
    if data is not None:
        answers.append(data)
    with inputs(*answers):
        show_sorting()
    assert "After:" in capsys.readouterr().out


def test_sort_menu_invalid(capsys):
    with inputs("9"):
        show_sorting()
    with inputs("1", "9"):
        show_sorting()
    assert capsys.readouterr().out.count("Unknown") == 2


def test_graph_menu_crud_and_iterators(capsys):
    graph = Graph()
    with inputs("1", "A", "1", "B", "2", "A", "B", "5", "A", "A", "B",
                "6", "A", "A", "B", "7", "A", "8", "4", "A", "B", "3", "B",
                "9", "v", "10", "0"):
        graph_menu(graph)
    assert graph.is_empty()
    output = capsys.readouterr().out
    assert "Vertex exists: True" in output
    assert "Vertex degree: 1" in output
    assert "Copy" in output or "copy == graph" in output


def test_graph_menu_erase_edge(capsys):
    graph = Graph()
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_edge("A", "B")
    with inputs("9", "e", "9", "e", "9", "unknown", "0"):
        graph_menu(graph)
    assert graph.edge_count() == 0
    assert "Error:" in capsys.readouterr().out


def test_graph_menu_error_and_unknown(capsys):
    graph = Graph()
    with inputs("2", "A", "B", "3", "A", "4", "A", "B", "6", "A", "A", "B",
                "7", "99", "0"):
        graph_menu(graph)
    assert "Error:" in capsys.readouterr().out


def test_show_empty_iterators(capsys):
    show_iterators(Graph())
    assert "Vertices: []" in capsys.readouterr().out


def test_read_and_select():
    with inputs("14"):
        assert read_int("Number: ") == 14
    graph = Graph()
    graph.add_vertex("A")
    iterator = next_selected(graph.iter_vertices())
    assert iterator.current == "A"


def test_main_flow(capsys):
    with inputs("9", "1", "9", "2", "0", "0"):
        main()
    assert "Goodbye" in capsys.readouterr().out


def test_main_bad_numeric(capsys):
    with inputs("1", "1", "1", "not-numbers", "0"):
        main()
    assert "Input error:" in capsys.readouterr().out
