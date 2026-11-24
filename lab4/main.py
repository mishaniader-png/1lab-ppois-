

from dataclasses import dataclass

from graph import Graph
from sorts import comb_sort, tournament_sort

#cd ~/Downloads/ppois_lab4_ready/lab4
#python -m pytest -q


@dataclass
class Student:
    name: str
    grade: int


def read_int(prompt):
    return int(input(prompt))


def show_sorting():
    print("\n1 - Comb Sort, 2 - Tournament Sort")
    choice = input("Algorithm: ").strip()
    algorithm = {"1": comb_sort, "2": tournament_sort}.get(choice)
    if algorithm is None:
        print("Unknown algorithm")
        return
    print("1 - integers, 2 - words, 3 - Students by grade")
    data_type = input("Data type: ").strip()
    if data_type == "1":
        data = [int(item) for item in input("Integers, space-separated: ").split()]
        key = None
    elif data_type == "2":
        data = input("Words, space-separated: ").split()
        key = None
    elif data_type == "3":
        data = [Student("Misha", 8), Student("Artem", 10), Student("Dima", 6)]
        key = lambda student: student.grade
    else:
        print("Unknown data type")
        return
    print("Before:", data)
    algorithm(data, key=key)
    print("After:", data)
    print("Built-in sorted():", sorted(data, key=key))


def show_iterators(graph):
    print("Vertices:", list(graph.iter_vertices()))
    print("Reverse vertices:", list(graph.iter_vertices(reverse=True)))
    print("Read-only vertices:", list(graph.iter_vertices(const=True)))
    print("Edges:", list(graph.iter_edges()))
    print("Reverse edges:", list(graph.iter_edges(reverse=True)))
    print("Read-only edges:", list(graph.iter_edges(const=True)))
    if graph.is_empty():
        return
    vertex = input("Vertex for adjacent/incident iterators: ")
    print("Adjacent:", list(graph.iter_adjacent_vertices(vertex)))
    print("Adjacent reverse:", list(graph.iter_adjacent_vertices(vertex, reverse=True, const=True)))
    print("Incident edges:", list(graph.iter_incident_edges(vertex)))
    print("Incident reverse:", list(graph.iter_incident_edges(vertex, reverse=True, const=True)))


def graph_menu(graph):
    while True:
        print("\nGraph:", graph)
        print("1 add vertex | 2 add edge | 3 remove vertex | 4 remove edge")
        print("5 check vertex/edge | 6 degrees | 7 iterators | 8 copy/compare")
        print("9 erase by iterator | 10 clear | 0 back")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                return
            if choice == "1":
                graph.add_vertex(input("Vertex value: "))
            elif choice == "2":
                graph.add_edge(input("First: "), input("Second: "))
            elif choice == "3":
                graph.remove_vertex(input("Vertex to remove: "))
            elif choice == "4":
                graph.remove_edge(input("First: "), input("Second: "))
            elif choice == "5":
                vertex = input("Vertex to check: ")
                first = input("First endpoint: ")
                second = input("Second endpoint: ")
                print("Vertex exists:", graph.has_vertex(vertex))
                print("Edge exists:", graph.has_edge(first, second))
                print("Count:", graph.vertex_count(), "vertices;", graph.edge_count(), "edges")
            elif choice == "6":
                vertex = input("Vertex for degree: ")
                first = input("Edge first endpoint: ")
                second = input("Edge second endpoint: ")
                print("Vertex degree:", graph.vertex_degree(vertex))
                print("Edge degree:", graph.edge_degree(first, second))
            elif choice == "7":
                show_iterators(graph)
            elif choice == "8":
                copy = graph.copy()
                other = Graph()
                other.assign_from(copy)
                print("Deep copy:", copy)
                print("copy == graph:", copy == graph)
                print("copy <= graph:", copy <= graph)
                print("copy >= graph:", copy >= graph)
                print("copy != graph:", copy != graph)
                print("copy < graph:", copy < graph)
                print("copy > graph:", copy > graph)
                print("assign_from equal:", other == graph)
            elif choice == "9":
                kind = input("Erase first vertex (v) or first edge (e): ").strip()
                if kind == "v":
                    iterator = graph.iter_vertices()
                    graph.remove_vertex_at(next_selected(iterator))
                elif kind == "e":
                    iterator = graph.iter_edges()
                    graph.remove_edge_at(next_selected(iterator))
                else:
                    print("Unknown iterator kind")
            elif choice == "10":
                graph.clear()
            else:
                print("Unknown option")
        except (ValueError, StopIteration, RuntimeError) as error:
            print("Error:", error)


def next_selected(iterator):
    next(iterator)
    return iterator


def main():
    graph = Graph()
    while True:
        print("\nLAB 4 | 1 - sorting | 2 - graph | 0 - exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                print("Goodbye")
                return
            if choice == "1":
                show_sorting()
            elif choice == "2":
                graph_menu(graph)
            else:
                print("Unknown option")
        except ValueError as error:
            print("Input error:", error)


if __name__ == "__main__":
    main()
