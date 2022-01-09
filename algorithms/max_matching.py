import market as Market
from algorithms import hungarian_algorithm as HA
import networkx as nx
from config import ALGORITHM, PRINT
from algorithms.LP.linear_program import solve_KEP

import time
import algorithms.kidney_solver.kidney_digraph as kidney_digraph
import algorithms.kidney_solver.kidney_ip as kidney_ip
import algorithms.kidney_solver.kidney_utils as kidney_utils
import algorithms.kidney_solver.kidney_ndds as kidney_ndds


class MaxMatching:
    """
    Finds maximum weight matching in a kidney exchange market, useing the hungarian algorithms
    The kidney exchange market is represented as a bipartite graph
    """

    def __init__(self, market, max_cycle_size, max_path_size):
        """
        :param market: a Market instance which is a kidney exchange market
        """
        self.bigraph = market
        self.cycle_lengths = None
        self.max_cycle_size = max_cycle_size
        self.max_path_size = max_path_size


    def maximum_matching(self):
        if ALGORITHM == "HA":
            return self.HA_maximum_matching()
        elif ALGORITHM == "LP":
            return self.LP_maximum_matching()
        elif ALGORITHM == "FAST":
            return self.FAST_maximum_matching()



    def HA_maximum_matching(self):
        """
        finds matching using the hungarian algorithm
        :return: a set of all the edges in the matching
        """
        edges = set()
        participant_list = self.bigraph.participants.copy()
        new_graph = self.bigraph.graph.copy()
        for participant in self.bigraph.participants:
            if participant.donor and len(participant.neighbours) == 0:
                to_remove = None
                for (p1, p2) in new_graph.edges():
                    if p2 == participant:
                        to_remove = p1
                        participant_list.remove(p1)
                if to_remove is not None:
                    new_graph.remove_node(to_remove)
                if participant in new_graph.nodes():
                    new_graph.remove_node(participant)
                participant_list.remove(participant)
        if len(participant_list) == 0:
            return edges
        matrix = (nx.adjacency_matrix(new_graph)).todense().tolist()
        for n in range(len(matrix)):
            matrix[n] = [-100000 if x == 0 else x for x in matrix[n]]
        # give a score of 1 between pairs
        for n in range(int(len(matrix) / 2)):
            matrix[(n * 2) + 1][(n*2)] = 1
            matrix[(n * 2)][n * 2 + 1] = 1
        matching = HA.max_weight_matching(matrix)
        if matching[2] <= (len(self.bigraph.participants) / 2):
            return edges
        else:
            # identify the participants in the matching
            for p in matching[0].keys():
                participant1 = participant_list[p]
                participant2 = participant_list[matching[0][p]]
                if not (participant1.partner == participant2):
                    edge = (participant1, participant2)
                    edges.add(edge)
            return edges

    def LP_maximum_matching(self):
        """
        finds a matching using a linear program
        :return: a set of all the edges in the matching
                 a set of all unmatched donors (that could be future altruists)
        """
        G, pair_dict, weights, _ = self.bigraph.get_adj_list()
        altruist_list = self.bigraph.get_alt_list()
        print("Altruists in this period:")
        for altruist in altruist_list:
            print(str(altruist) + ':', end=" ")
            print(G[altruist])
        OPT, cpu_time, _, _, _, chains, cycles = solve_KEP(G, self.max_cycle_size, self.max_path_size, altruist_list, weights=weights)
        print("-----------------------------------------------------")
        # Now track all removed pairs
        edges = set()
        preserved_donors = set() # preserve the donor of last pair in a chain
        cycle_path_lengths = ([0, 0, 0, 0, 0], [0])  # number of cycle lengths, and number of matches in chains
        for chain in chains:
            for i in range(len(chain)-1):
                edge1 = chain[i]
                p1 = pair_dict[edge1[0]]
                p2 = pair_dict[edge1[1]]  # both p1 and p2 are donor
                match1 = (p1.partner, p1)
                match2 = (p1, p2.partner)
                edges.add(match1)
                edges.add(match2)
                cycle_path_lengths[1][0] += 1
            i = len(chain)-1
            edge = chain[i]
            p1 = pair_dict[edge[0]]
            p2 = pair_dict[edge[1]]  # this is the preserved donor
            match1 = (p1.partner, p1)
            match2 = (p1, p2.partner)
            edges.add(match1)
            edges.add(match2)
            preserved_donors.add(p2)
            match3 = (p2.partner, p2)
            edges.add(match3)
            cycle_path_lengths[1][0] += 1

        for cycle in cycles:
            for i in range(len(cycle) - 1):
                pair1 = pair_dict[cycle[i]]
                pair2 = pair_dict[cycle[i+1]]  # both pair1 and pair2 are donors
                edge1 = (pair1.partner, pair1)  # the 1st edge is the rec. pointing to the donor in the same pair
                edge2 = (pair1, pair2.partner)
                edges.add(edge1)
                edges.add(edge2)
            pair1 = pair_dict[cycle[(len(cycle) - 1)]]
            pair2 = pair_dict[cycle[0]]
            edge1 = (pair1.partner, pair1)
            edge2 = (pair1, pair2.partner)
            edges.add(edge1)
            edges.add(edge2)
            if len(cycle) > 6:
                cycle_path_lengths[0][4] += 1
            else:
                cycle_path_lengths[0][len(cycle) - 2] += 1
        self.cycle_lengths = cycle_path_lengths
        return edges, preserved_donors


    def FAST_maximum_matching(self):
        """
        finds a matching using a faster linear program -- kidney_solver_master
        in the original algorithm, it takes input of 2 files: .input and .ndds
        need to mimic files for both .input and .ndds from our model:P
        digraph_lines <==> .input   &   ndd_lines <==> .ndds
        :return: a set of all the edges in the matching
        """

        G, pair_dict, weights, vertex_list = self.bigraph.get_adj_list()
        altruist_list = self.bigraph.get_alt_list()
        print("Altruist in this period:", end=" ")
        print(altruist_list)

        # initialize .input
        digraph_lines = list()
        new_keys = list()  # a list of keys that excludes altruists
        for key in G.keys():
            if key in altruist_list:
                continue
            else:
                new_keys.append(key)
        temp_list = list()  # a list of all the neighbors of altruists
        for alt in altruist_list:
            for v in G[alt]:
                temp_list.append(v)
        digraph_lines.append(str(len(new_keys)) + "\t" + str(len(weights)-len(temp_list)) + "\n")
        for key in new_keys:
            for val in G[key]:
                digraph_lines.append(str(key) + "\t" + str(val) + "\t" + str(weights[(key, val)]) + "\n")
        digraph_lines.append(str(-1) + "\t" + str(-1) + "\t" + str(-1) + "\n")

        d = kidney_digraph.read_digraph(digraph_lines, vertices=vertex_list)

        #initialize .ndds
        ndd_lines = list()
        i = 0
        ndd_lines.append(str(len(altruist_list)) + "\t" + str(len(temp_list)) + "\n")
        for key in altruist_list:
            for val in G[key]:
                ndd_lines.append(str(i) + "\t" + str(val) + "\t" + str(weights[(key, val)]) + "\n")
            i = i+1
        ndd_lines.append(str(-1) + "\t" + str(-1) + "\t" + str(-1) + "\n")

        altruists = kidney_ndds.read_ndds(ndd_lines, d)

        start_time = time.time()
        cfg = kidney_ip.OptConfig(d, altruists, self.max_cycle_size, self.max_path_size)
        opt_solution = solve_kep(cfg, formulation="picef", use_relabelled=False)
        time_taken = time.time() - start_time
        if (PRINT):
            print("formulation: PICEF")
            print("cycle_cap: %s" % str(self.max_cycle_size))
            print("chain_cap: %s" % str(self.max_path_size))
            print(("ip_vars: {}".format(opt_solution.ip_model.numVars)))
            print(("ip_constrs: {}".format(opt_solution.ip_model.numConstrs)))
            print(("total_time: {}".format(time_taken)))
            print(("ip_solve_time: {}".format(opt_solution.ip_model.runtime)))
            print(("solver_status: {}".format(opt_solution.ip_model.status)))
            print(("total_score: {}".format(opt_solution.total_score)))
        cycles, chains = opt_solution.display(altruist_list)  # Note that in each chain array, altruist is excluded
        print("-------------------------------------------------------")
        edges = set()
        preserved_donors = set()  # preserve the donor of last pair in a chain
        cycle_path_lengths = [[0, 0, 0, 0, 0], [0], [0, 0, 0, 0, 0]]  # cycle matches by size, path matches, path matches by size (0-5, 6-10, 11-15, 16-20, 21+)
        j = 0  # keep track of index of chain in chains
        for chain in chains:
            # update cycle_path_lengths
            cycle_path_lengths[1][0] += len(chain)
            if len(chain) <= 5:
                cycle_path_lengths[2][0] += 1
            elif len(chain) <= 10:
                cycle_path_lengths[2][1] += 1
            elif len(chain) <= 15:
                cycle_path_lengths[2][2] += 1
            elif len(chain) <= 20:
                cycle_path_lengths[2][3] += 1
            else:
                cycle_path_lengths[2][4] += 1
            # remove altruist
            a = pair_dict[altruist_list[j]]  # this is the donor
            p = pair_dict[chain[0]]
            pair1 = (a.partner,a)
            pair2 = (a, p)
            edges.add(pair1)
            edges.add(pair2)
            # remove the rest
            for i in range(len(chain)-1):
                p1 = pair_dict[chain[i]]
                p2 = pair_dict[chain[i+1]]
                pair1 = (p1.partner, p1)
                pair2 = (p1, p2.partner)
                edges.add(pair1)
                edges.add(pair2)
            i = len(chain)-1
            p = pair_dict[chain[i]]  # last one in the chain is a potential preserved donor
            preserved_donors.add(p)
            pair = (p.partner, p)
            edges.add(pair)
            j += 1

        for cycle in cycles:
            for i in range(len(cycle) - 1):
                pair1 = pair_dict[cycle[i]]
                pair2 = pair_dict[cycle[i + 1]] # both are donors
                edge1 = (pair1.partner, pair1)
                edge2 = (pair1, pair2.partner)
                edges.add(edge1)
                edges.add(edge2)
            pair1 = pair_dict[cycle[(len(cycle) - 1)]]
            pair2 = pair_dict[cycle[0]]
            edge1 = (pair1.partner, pair1)
            edge2 = (pair1, pair2.partner)
            edges.add(edge1)
            edges.add(edge2)
            if len(cycle) > 6:
                cycle_path_lengths[0][4] += 1
            else:
                cycle_path_lengths[0][len(cycle) - 2] += 1
        self.cycle_lengths = cycle_path_lengths
        return edges, preserved_donors


def solve_kep(cfg, formulation, use_relabelled=True):
    formulations = {
        "uef": ("Uncapped edge formulation", kidney_ip.optimise_uuef),
        "eef": ("EEF", kidney_ip.optimise_eef),
        "eef_full_red": ("EEF with full reduction by cycle generation", kidney_ip.optimise_eef_full_red),
        "hpief_prime": ("HPIEF'", kidney_ip.optimise_hpief_prime),
        "hpief_prime_full_red": (
        "HPIEF' with full reduction by cycle generation", kidney_ip.optimise_hpief_prime_full_red),
        "hpief_2prime": ("HPIEF''", kidney_ip.optimise_hpief_2prime),
        "hpief_2prime_full_red": (
        "HPIEF'' with full reduction by cycle generation", kidney_ip.optimise_hpief_2prime_full_red),
        "picef": ("PICEF", kidney_ip.optimise_picef),
        "cf": ("Cycle formulation",
               kidney_ip.optimise_ccf)
    }

    if formulation in formulations:
        formulation_name, formulation_fun = formulations[formulation]
        if use_relabelled:
            opt_result = kidney_ip.optimise_relabelled(formulation_fun, cfg)
        else:
            opt_result = formulation_fun(cfg)
        kidney_utils.check_validity(opt_result, cfg.digraph, cfg.ndds, cfg.max_cycle, cfg.max_chain)
        opt_result.formulation_name = formulation_name
        return opt_result
    else:
        raise ValueError("Unrecognised IP formulation name")



