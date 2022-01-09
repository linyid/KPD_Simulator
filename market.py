import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as random
from config import PERIOD_LENGTH, PERISH, WEIGHTS, ALGORITHM, REUSE_RATE,TIME_TO_CRITICAL_LOW,ALT_WEIGHT, START_SIZE,ARRIVAL_RATE, NUM_PERIODS
import algorithms.max_matching as mm
import market_metrics as met
from participant import Participant
import statistics




class Market:
    """
    A kidney paired donation market represented as a bipartite graph
    Participants are the nodes of the graph and edges represent potential kidney exchanges
    Attributes
    ----------
    participants: list<(Participant, Participant)>
        a list of all the participants in the market
    graph: Digraph
        a networkx directed graph
    metrics: Metrics
        a Metrics instance, which tracks all the stats for the market
    altruists: list<(Participant, Participant)>
        a list of all the altruists in the market
    """

    def __init__(self, pairs, num_altruists, per_period, weights=None, run_num=-1, max_cycle_size=3, max_path_size=3):
        self.random_state = random.RandomState()
        self.graph = nx.DiGraph()
        self.participants = list()
        self.metrics = met.Metrics(num_altruists=num_altruists, per_period=per_period, weights=weights, run_num=run_num, max_cycle_size=max_cycle_size, max_path_size=max_path_size)
        for (recipient, donor) in pairs:
            self.add_pair((recipient, donor))
        self.altruists = list()
        self.num_added = 0
        self.total_wait_time = 0
        self.wait_times = list()
        self.max_cycle_size = max_cycle_size
        self.max_path_size = max_path_size



    def run_period(self, new_participants=list(), new_altruists=list(), period_num=-1, seed = -1, test_trial_num = None, trial_table = None):
        """
        Runs the matching algorithms for one period
        Updates the market at the end of the period
        :param new_participants: the new agents to add to the market at the end of the matching
        """
        # Run matching algorithms
        self.update(added_pairs=list(), matched_pairs=list(), altruists=new_altruists, update_time = False)
        bigraph = mm.MaxMatching(self, max_cycle_size=self.max_cycle_size, max_path_size=self.max_path_size)
        matches, preserved_donors = bigraph.maximum_matching()
        cycle_path_lengths = bigraph.cycle_lengths
        num_altruists_in_matching = 0
        # Count how many altruists are in the matching
        for match in matches:
            if match[0].blood_type == 'X':
                num_altruists_in_matching += 1
        median = 0
        if len(self.wait_times) > 0:
            median = statistics.median(self.wait_times)
            print("THE median is " + str(median))
            print(self.wait_times)
            print("-----------------------------------------------------")
            print()
        if ALGORITHM == "HA":
            num_matches = len(matches) - num_altruists_in_matching
        else:
            num_matches = 0
            for i in range(0,5):
                num_matches = num_matches + (i+2)*cycle_path_lengths[0][i]
            num_matches = num_matches + cycle_path_lengths[1][0]
        # preserved donor becomes new altruists
        if REUSE_RATE != 0:
            for donor in preserved_donors:
                use = np.random.choice([False, True], p=[1-REUSE_RATE, REUSE_RATE])
                if not use:
                   continue
                donor.altruist = True
                time_to_critical = int(np.random.poisson(lam=TIME_TO_CRITICAL_LOW, size=1))
                recipient = Participant(donor.id_num, blood_type='X', donor=False, recipient=True, altruist = True,
                                       time_to_critical=time_to_critical, weight=ALT_WEIGHT, cpra=0, dialysis_days=0)
                new_altruist = (recipient,donor)
                new_altruists.append(new_altruist)
        self.update(added_pairs=new_participants, matched_pairs=matches, altruists=list(),update_time = True)
        self.num_added = len(new_participants)
        total_unmatched_time = 0
        if period_num + 1 == NUM_PERIODS:
            for p in self.participants:
                if p.recipient and p.blood_type != "X":
                    total_unmatched_time += p.time_in_market

        # update table
        if trial_table is None:
            self.metrics.update_table(num_matches=num_matches, num_participants=len(self.participants), num_added=self.num_added, num_altruists_in_market=len(self.altruists), num_altruists_in_matching=num_altruists_in_matching, total_wait_time=self.total_wait_time, median_wait_time=median, total_remaining_time=total_unmatched_time, cycle_lengths=cycle_path_lengths, wait_times=self.wait_times)
        else:
            if test_trial_num == 1:
                self.metrics.initialize_trial_table(trial_table=trial_table)
            self.metrics.update_trial_table(num_matches=num_matches, num_participants=len(self.participants),
                                      num_added=self.num_added, num_altruists_in_market=len(self.altruists),
                                      num_altruists_in_matching=num_altruists_in_matching,
                                      total_wait_time=self.total_wait_time, median_wait_time=median,
                                      total_remaining_time=total_unmatched_time, seed_num= seed,
                                      trial_num = test_trial_num, cycle_lengths=cycle_path_lengths,
                                      wait_times=self.wait_times, trial_table=trial_table)

        print("There remains {} pairs in the market (excluding altruists)".format(len(self.participants)/2))

        return cycle_path_lengths



    def add_participant(self, participant):
        """
        adds a participant to the market
        :param participant: a participant to add to the market
        """
        if not (participant in list(self.graph.nodes())):
            self.add_node_to_graph(participant)
        if participant.donor:
            for p in self.participants:
                if p.recipient and participant.compatible(p,self.random_state) and (not participant.partner == p):
                    participant.add_neighbour(p)
                    weight = p.weight
                    # penalize for altruist-patient edge
                    if participant.altruist:
                        weight = weight + ALT_WEIGHT
                    if WEIGHTS == "KPD":
                        weight = calculate_kpd_weight(donor=participant, recipient=p)
                        if participant.altruist:
                            print("altruist weight is = ", weight)
                    # weight is determined by the recipient when determining who to match
                    self.graph.add_weighted_edges_from([(participant, p, weight)])
        # participant is patient
        else:
            for p in self.participants:
                if participant.blood_type == "X":
                    break
                if p.donor and participant.compatible(p, self.random_state) and (not participant.partner == p):
                    p.add_neighbour(participant)
                    weight = participant.weight
                    # penalize for altruist-patient edge
                    if p.altruist:
                        weight = weight + ALT_WEIGHT
                    if WEIGHTS == "KPD":
                        weight = calculate_kpd_weight(donor=p, recipient=participant)
                        if p.altruist:
                            print("altruist weight is = ", weight)
                    # weight is determined by the recipient when determining who to match
                    self.graph.add_weighted_edges_from([(p, participant, weight)])

    def add_node_to_graph(self, participant):
        """
        adds a participant to the networkx bipartite graph
        :param participant: participant to add to the graph
        """
        if participant.donor:
            self.graph.add_nodes_from([participant], bipartite=1)
        elif participant.recipient:
            self.graph.add_nodes_from([participant], bipartite=0)
        self.participants.append(participant)

    def remove_participant(self, participant):
        """
        removes a participant from the market
        :param participant: a participant to remove from the market
        """
        # avoid removing a participant more than once
        if participant not in self.participants:
            return
        if participant.donor:
            # only update metrics for donors, so we don't update more than once
            self.metrics.update_blood_type_composition((participant.partner, participant), remove=True)
            self.metrics.update_cpra_composition((participant.partner, participant), remove=True)
            for p in self.participants:
                if p.recipient:
                    participant.remove_neighbour(p)
            if (participant.partner, participant) in self.altruists:
                self.altruists.remove((participant.partner, participant))
        else:
            for p in self.participants:
                if p.donor:
                    p.remove_neighbour(participant)
            if (participant, participant.partner) in self.altruists:
                self.altruists.remove((participant, participant.partner))
        if participant in self.graph.nodes():
            self.graph.remove_node(participant)
        self.participants.remove(participant)


    def draw_market(self):
        if len(self.graph.nodes()) > 0:
            graph_pos = nx.spring_layout(self.graph, k=(1 / (0.9 * np.sqrt(len(
                self.graph.nodes())))))
        else:
            graph_pos = nx.spring_layout(self.graph, k=0)
        plt.clf()
        plt.axis('off')
        my_labels = {}
        colours = list()
        for participant in self.participants:
            my_labels[participant] = participant.blood_type
            if participant.donor:
                colours.append('y')
            elif participant.recipient:
                colours.append('g')
            else:
                colours.append('b')
        nx.draw_networkx(self.graph, pos=graph_pos, with_labels=True, node_size=1000, node_color=colours, labels=my_labels,
                         font_size=7.5, font_weight='bold')
        plt.show()

    def add_pair(self, pair):
        """
        adds a patient-donor pair to the market
        pair is a tuple in the form (recipient, participant)
        :param recipient: Participant - the recipient of the patient-donor pair
        :param donor: Participant - the donor of the patient-donor pair
        """
        pair[0].add_neighbour(pair[1])
        pair[0].partner = pair[1]
        pair[1].partner = pair[0]
        self.add_participant(pair[1])
        self.add_participant(pair[0])
        self.graph.add_weighted_edges_from([(pair[0], pair[1], 1)])
        self.metrics.update_blood_type_composition(pair, remove=False)
        self.metrics.update_cpra_composition(pair, remove=False)

    def get_adj_list2(self):
        """
        gets the adjacency matrix of the bipartite graph of this market
        :return: the adjacency matrix
        """
        return nx.adjacency_matrix(self.graph)

    def to_bipartite(self):
        """
        creates a bipartite graph
        :return: bipartite graph
        """
        donors = list(filter(lambda x: x.donor, self.participants))
        recipients = list(filter(lambda x: x.recipient, self.participants))
        B = nx.DiGraph()
        B.add_nodes_from(recipients, bipartite=0)
        B.add_nodes_from(donors, bipartite=1)
        for participant in self.participants:
            for neighbour in participant.neighbours:
                if participant.recipient:
                    B.add_weighted_edges_from([(participant, neighbour, 0)])
                else:
                    B.add_weighted_edges_from([(participant, neighbour, 1)])
        return B

    def remove_perished(self):
        """
        removes pairs from the market that have been in the market for their time_to_critical amount of time
        """
        participants = self.participants
        perished = list()
        for p in participants:
            if p.time_in_market >= p.time_to_critical:
                perished.append(p)
        for p in perished:
            self.remove_participant(p)

    def update(self, added_pairs=list(), matched_pairs=list(), altruists=list(), update_time=False):
        """
        updates the market by adding pairs, removing perished pairs, removing matched pairs, and adding altruists
        :param added_pairs: a list of tuples of participants in the form (recipiant, donor) that are to be added to the market
        :param matched_pairs: a list of pairs that need to be removed from the market
        :param altruists: a list of altruists to add to the market
        :param update_time: indicate weather we want to update the waiting time or not
        :return:
        """
        if update_time:
            for p in self.participants:
                p.time_in_market = p.time_in_market + PERIOD_LENGTH
                if p.recipient:
                    p.dialysis_days = p.dialysis_days + 30 * PERIOD_LENGTH
        if PERISH & update_time:
            self.remove_perished()
        for pair in added_pairs:
            self.add_pair(pair)
        for pair in matched_pairs:
            if pair[0].recipient and (pair[0].blood_type!="X") and update_time:
                self.wait_times.append(pair[0].time_in_market)
                self.total_wait_time = self.total_wait_time + pair[0].time_in_market
            self.remove_participant(pair[0])
            self.remove_participant(pair[1])
            if pair in altruists:
                self.altruists.remove(pair)
        for a in altruists:
            self.add_pair(a)
            self.altruists.append(a)


    def get_adj_list(self):
        """
        Creates an adjacency list of all the participants in the market
        Each patient-donor pair is represented with their unique id_num
        :return: a dictionary where the id_nums are keys and the values are
        the id_nums of the patients that the donor points to and a dictionary of
        all the pair id and their pairs
        """
        # pairs are the keys
        weights_list = {}
        adj_list = {}
        pair_dict = {}
        vertex_list = list()
        for participant in self.participants:
            if participant.donor:
                neigh_list = list()
                for patient in participant.neighbours:
                    neigh_list.append(patient.id_num)
                    if WEIGHTS == 'KPD':
                        weight = calculate_kpd_weight(participant, patient)
                    else:
                        weight = patient.weight
                        if participant.altruist:
                            weight += ALT_WEIGHT
                    weights_list[(participant.id_num, patient.id_num)] = weight
                adj_list[participant.id_num] = neigh_list
                pair_dict[participant.id_num] = participant
            if participant.id_num not in vertex_list:
                vertex_list.append(participant.id_num)
        return adj_list, pair_dict, weights_list, vertex_list

    def get_alt_list(self):
        """
        :return: a list of the id_nums of all altruists
        """
        alt_list = list()
        for alt in self.altruists:
            alt_list.append(alt[1].id_num)
        return alt_list


def calculate_kpd_weight(donor, recipient):
        """
        calculates the weight of the edge connecting the donor to the recipient
        this is the weight that the current canadian KPD program uses
        :param donor: a participant object
        :param recipient: a recipient object
        :return: the weight as an float
        """
        
        weight = 100
        if recipient.cpra >= 0.80:
            weight += 125
        #if recipient.age <= 18:
            #weight += 75
        #if recipient.province == donor.province:
           # weight += 25
        #if abs(recipient.age - donor.age) <= 30:
            #weight += 5
        #weight += recipient.dialysis_days/30
        if recipient.blood_type == 'O' and donor.blood_type == 'O':
            weight += 75
        elif donor.blood_type == recipient.blood_type:
            weight += 5
        if donor.altruist:
            weight += ALT_WEIGHT
        return int(weight)

