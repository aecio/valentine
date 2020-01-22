from propagation_graph import PropagationGraph
from utils import NodePair
import Levenshtein as lv
import math


class SimilarityFlooding:

    def __init__(self, graph1, graph2, coeff_policy, formula):
        self.graph1 = graph1
        self.graph2 = graph2
        self.propagation_graph = None
        self.coeff_policy = coeff_policy
        self.formula = formula  # formula used to update similarities of map-pairs as shown in page 10 of the paper
        self.initial_map = None

    def calculate_initial_mapping(self):
        
        self.initial_map = {}

        for n1 in self.graph1.nodes():
            for n2 in self.graph2.nodes():
                if n1.name[0:6] == "NodeID" or n2.name[0:6] == "NodeID":
                    self.initial_map[NodePair(n1, n2)] = 0.0
                else:
                    similarity = lv.ratio(n1.name, n2.name)
                    self.initial_map[NodePair(n1, n2)] = similarity

    def fixpoint_computation(self, num_iter, residual_diff):

        '''

        :param num_iter: maximum number of iterations
        :param error: error bound for stopping the iterative process
        :return: a dictionary with all similarities of all map pairs
        '''

        PGbuilder = PropagationGraph(self.graph1, self.graph2, self.coeff_policy)

        PG = PGbuilder.construct_graph()

        if self.formula == 'basic':  # using the basing formula

            previous_map = self.initial_map.copy()
            next_map = {}
            for i in range(0,num_iter):
                maxmap = 0
                for n in PG.nodes():
                    map_sim = previous_map[n]
                    
                    for e in PG.in_edges(n):
                        l = PG.get_edge_data(e[0],e[1])
                        
                        weight = l.get('weight')
                        
                        map_sim += weight*previous_map[e[0]]
                        
                    if map_sim > maxmap:
                        maxmap = map_sim
                    
                    next_map[n] = map_sim
                for key in next_map.keys():
                    next_map[key] = next_map[key]/maxmap

                # residual vector
                residual_vector = {key: math.pow(previous_map.get(key, 0) - next_map.get(key, 0),2) for key in set(previous_map) | set(next_map)}

                euc_len = math.sqrt(sum(residual_vector.values()))  # compute euclidean length of residual vector

                if euc_len <= residual_diff:  # check whether the algo has converged
                    break

                previous_map = next_map.copy()
                next_map = {}
        elif self.formula == 'formula_a':  # using formula A
            previous_map = self.initial_map.copy()
            next_map = {}
            for i in range(0,num_iter):
                maxmap = 0
                for n in PG.nodes():
                    map_sim = self.initial_map[n]

                    for e in PG.in_edges(n):
                        l = PG.get_edge_data(e[0],e[1])

                        weight = l.get('weight')

                        map_sim += weight*previous_map[e[0]]

                    if map_sim > maxmap:
                        maxmap = map_sim

                    next_map[n] = map_sim
                for key in next_map.keys():
                    next_map[key] = next_map[key]/maxmap

                # residual vector
                residual_vector = {key: math.pow(previous_map.get(key, 0) - next_map.get(key, 0),2) for key in set(previous_map) | set(next_map)}

                euc_len = math.sqrt(sum(residual_vector.values()))  # compute euclidean length of residual vector

                if euc_len <= residual_diff:  # check whether the algo has converged
                    break

                previous_map = next_map.copy()
                next_map = {}
        elif self.formula == 'formula_b':  # using formula B
            next_map = {}
            maxmap = 0
            for n in PG.nodes():
                map_sim = 0

                for e in PG.in_edges(n):
                    l = PG.get_edge_data(e[0],e[1])

                    weight = l.get('weight')

                    map_sim += weight*self.initial_map[e[0]]

                if map_sim > maxmap:
                    maxmap = map_sim

                next_map[n] = map_sim
            for key in next_map.keys():
                next_map[key] = next_map[key]/maxmap
            previous_map = next_map.copy()
            next_map = {}

            for i in range(0, num_iter-1):
                maxmap = 0
                for n in PG.nodes():
                    map_sim = 0

                    for e in PG.in_edges(n):
                        l = PG.get_edge_data(e[0],e[1])

                        weight = l.get('weight')

                        map_sim += weight*(previous_map[e[0]]+self.initial_map[e[0]])

                    if map_sim > maxmap:
                        maxmap = map_sim

                    next_map[n] = map_sim
                for key in next_map.keys():
                    next_map[key] = next_map[key]/maxmap

                # residual vector
                residual_vector = {key: math.pow(previous_map.get(key, 0) - next_map.get(key, 0),2) for key in set(previous_map) | set(next_map)}

                euc_len = math.sqrt(sum(residual_vector.values()))  # compute euclidean length of residual vector

                if euc_len <= residual_diff:  # check whether the algo has converged
                    break

                previous_map = next_map.copy()
                next_map = {}
        elif self.formula == 'formula_c':  # using formula C which is claimed to be the best one
            next_map = {}
            maxmap = 0
            for n in PG.nodes():
                map_sim = self.initial_map[n]

                for e in PG.in_edges(n):
                    l = PG.get_edge_data(e[0],e[1])

                    weight = l.get('weight')

                    map_sim += weight*self.initial_map[e[0]]

                if map_sim > maxmap:
                    maxmap = map_sim

                next_map[n] = map_sim
            for key in next_map.keys():
                next_map[key] = next_map[key]/maxmap
            previous_map = next_map.copy()
            next_map = {}

            for i in range(0, num_iter-1):
                maxmap = 0
                for n in PG.nodes():
                    map_sim = previous_map[n]

                    for e in PG.in_edges(n):
                        l = PG.get_edge_data(e[0],e[1])

                        weight = l.get('weight')

                        map_sim += self.initial_map[e[0]] + weight*(previous_map[e[0]]+self.initial_map[e[0]])

                    if map_sim > maxmap:
                        maxmap = map_sim

                    next_map[n] = map_sim
                for key in next_map.keys():
                    next_map[key] = next_map[key]/maxmap

                # residual vector
                residual_vector = {key: math.pow(previous_map.get(key, 0) - next_map.get(key, 0),2) for key in set(previous_map) | set(next_map)}

                euc_len = math.sqrt(sum(residual_vector.values()))  # compute euclidean length of residual vector

                if euc_len <= residual_diff:  # check whether the algo has converged
                    break

                previous_map = next_map.copy()
                next_map = {}
        else:
            print("Wrong formula option!")
            return {}

        return previous_map  # the dictionary storing the final similarities of map pairs

    def filter_map(self, prevmap):

        '''
        Function that filters the matching results, so that only pairs of columns remain
        :param prevmap: the matching results of the iterative algorithm
        :return: the filtered matchings
        '''

        filtered_map = prevmap.copy()

        for key in prevmap.keys():

            flag = False
            if key.node1.name[0:6] == 'NodeID':

                if key.node1 in self.graph1.nodes():

                    for e in self.graph1.out_edges(key.node1):

                        if e[1].name == 'Column':
                            flag = True

                            break
                else:

                    for e in self.graph2.out_edges(key.node1):

                        if e[1].name == 'Column':
                            flag = True

                            break
            else:

                del filtered_map[key]
                continue

            if flag:

                flag = False

                if key.node2.name[0:6] == 'NodeID':

                    if key.node2 in self.graph1.nodes():

                        for e in self.graph1.out_edges(key.node2):

                            if e[1].name == 'Column':
                                flag = True

                                break
                    else:
                        for e in self.graph2.out_edges(key.node2):

                            if e[1].name == 'Column':
                                flag = True

                                break
            else:

                del filtered_map[key]
                continue

            if not flag:

                del filtered_map[key]

        return filtered_map

    def print_results(self, matches):

        '''

        :param matches: dictionary holding the match similarities of map pairs

        '''

        sortedmaps = {k: v for k, v in sorted(matches.items(), key=lambda item: item[1])}

        for key in sortedmaps.keys():
            name1 = key.node1.name
            if key.node1.name[0:6] == 'NodeID':
                name1 = "[" + key.node1.name + "=>"
                if key.node1 in self.graph1.nodes():
                    for e in self.graph1.out_edges(key.node1):
                        l = self.graph1.get_edge_data(e[0],e[1])
                        name1 += l.get('label') + ":" + e[1].name + ", "
                else:
                    for e in self.graph2.out_edges(key.node1):
                        l = self.graph2.get_edge_data(e[0],e[1])
                        name1 += l.get('label') + e[1].name + ", "
                name1 += ']'

            name2 = key.node2.name
            if key.node2.name[0:6] == 'NodeID':
                name2 = "[" + key.node2.name + "=>"
                if key.node2 in self.graph1.nodes():
                    for e in self.graph1.out_edges(key.node2):
                        l = self.graph1.get_edge_data(e[0],e[1])
                        name2 += l.get('label') + ":" + e[1].name + ", "
                else:
                    for e in self.graph2.out_edges(key.node2):
                        l = self.graph2.get_edge_data(e[0],e[1])
                        name2 += l.get('label') + ":" + e[1].name + ", "
                name2 += ']'
            print(name1 + "-" + name2 + ":" + str(sortedmaps[key]))