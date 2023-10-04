import pulp
import networkx as nx
from fractions import Fraction

def initialise_graph(file_name):
    matrix = list()
    # reads text file
    with open(file_name) as file:
        for line in file:
            if line != '\n':
                matrix.append(line.split())
    edges = list()
    # gets edges from text file
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == '1':
                edges.append({i, i+j+1})
    # gets number of vertices
    num_vertices = len(matrix) + 1
    # initialises graph
    graph = nx.Graph(edges)
    graph.add_nodes_from(range(num_vertices))
    return graph

def first_lp(graph):
    # gets set of all cliques
    cliques_list = list(nx.enumerate_all_cliques(graph))
    cliques_set = list()
    for clique in cliques_list:
        cliques_set.append(set(clique))

    xs_array = list()
    # initialises variables
    for i in range(len(cliques_set)):
        xs = pulp.LpVariable("x" + str(i), lowBound=0)
        xs_array.append(xs)
    lp = pulp.LpProblem("Fractional clique cover number", pulp.LpMinimize)
    # objective function
    lp += pulp.lpSum(xs_array[i] for i in range(len(xs_array)))
    # applies constraint
    for vertex in graph.nodes():
        lp += pulp.lpSum(xs_array[i] for i in range(len(cliques_set)) if vertex in cliques_set[i]) >= 1
    lp.solve()
    return lp, xs_array

def second_lp(graph):
    # gets power set
    power_set = [set()]
    for element in graph.nodes:
        one_element_set = {element}
        power_set += [subset | one_element_set for subset in power_set]

    xv_array = list()
    # initialises variables (also applies constraint 1 and 2)
    for i in range(len(power_set)):
        if len(power_set[i]) > 1:
            xv = pulp.LpVariable("x" + str(i), lowBound=0)
        elif len(power_set[i]) == 1:
            xv = pulp.LpVariable("x" + str(i), lowBound=0, upBound=1)
        else:
            xv = pulp.LpVariable("x" + str(i), lowBound=0, upBound=0)

        xv_array.append(xv)
    lp = pulp.LpProblem("Shannon entropy", pulp.LpMaximize)
    # objective function
    lp += xv_array[-1:][0]

    # applies constraint 3
    for vertex in range(len(graph.nodes)):
        neighbours = set(graph.neighbors(vertex))
        neighbours_index = power_set.index(neighbours)
        union_index = power_set.index(neighbours.union({vertex}))
        lp += xv_array[union_index] - xv_array[neighbours_index] == 0

    # applies constrain 4 and 5
    for subset1 in range(len(power_set)):
        for subset2 in range(min(subset1+1, len(power_set)), len(power_set)):
            if power_set[subset2] >= power_set[subset1]:
                lp += xv_array[subset2] - xv_array[subset1] >= 0
            elif power_set[subset2] != power_set[subset1]:
                union = power_set[subset1].union(power_set[subset2])
                intersection = power_set[subset1].intersection(power_set[subset2])
                union_index = power_set.index(union)
                intersection_index = power_set.index(intersection)
                lp += xv_array[subset1] + xv_array[subset2] - xv_array[union_index] - xv_array[intersection_index] >=0
    lp.solve()
    return lp, xv_array

def save_output(file_name, xs_solution, xv_solution, xs_array, xv_array):
    # gets values in rational form
    xs_optimum = Fraction(xs_solution.objective.value()).limit_denominator()
    xv_optimum = Fraction(xv_solution.objective.value()).limit_denominator()
    with open(file_name[:-4] + '_xs_solution.txt', 'w') as file:
        # writes objective function to file in rational format
        file.write('fractional clique cover number value: ' + str(xs_optimum) + '\n')
        # writes variable values to file in rational format
        file.write('fractional clique cover number solution:\n')
        for xs in xs_array:
            file.write(str(xs) +': ' + str(Fraction(xs.value()).limit_denominator()) + '\n')
    with open(file_name[:-4] + '_xv_solution.txt', 'w') as file:
        # writes objective function to file in rational format
        file.write('shannon entropy value: ' + str(xv_optimum) + '\n')
        # writes variable values to file in rational format
        file.write('shannon entropy solution:\n')
        for xv in xv_array:
            file.write(str(xv) +': ' + str(Fraction(xv.value()).limit_denominator()) + '\n')
    print('\n')
    # outputs that the solutions have been saved
    print('fractional clique cover number solution saved to ' + file_name[:-4] + '_xs_solution.txt')
    print('shannon entropy solution saved to ' + file_name[:-4] + '_xv_solution.txt')
    print('\n')


if __name__ == "__main__":
    file_name = input('input graph file: ')
    # makes graph from text file
    graph = initialise_graph(file_name)
    # solves first LP
    xs_solution, xs_array = first_lp(graph)
    # solves second LP
    xv_solution, xv_array = second_lp(graph)
    print('\n')
    # outputs objective values
    print('fractional clique cover number value: ' + str(Fraction(xs_solution.objective.value()).limit_denominator()))
    print('shannon entropy value: ' + str(Fraction(xv_solution.objective.value()).limit_denominator()))
    # saves output
    save_output(file_name, xs_solution, xv_solution, xs_array, xv_array)



























