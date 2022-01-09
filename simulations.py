import numpy as np
from market import Market
from population import Population
from config import START_SIZE, NUM_PERIODS, ARRIVAL_RATE, CYCLE_CAP, CHAIN_CAP, RANDOM_SAMPLE
import testaltruists as ta
import testweights as tw
import testcyclesize as tcs


class Simulations:
    """
    Initializes and runs simulations, with a certain number of altruists and participants
    ----------
    population: Population
        a population from which new participants are created
    altruists: int
        a mean parameter of # altruists that enter the market every "per_period" periods
    per_period: int
        altruists enter the market every "per_period"
    market: Market
        the kidney exchange market that we run simulations on
    cycle_chain_matches:
        an array [x,x] keep track of matches by cycles and chains (don't include cycle size >6 now)
    test_trial_num:
        int if this is a test using different seeds, indicating the number of trial
        None if this is not a trial test using different seeds
    trial_table:
        xslx Worksheet object for seed trial test
    """
    def __init__(self, altruists, per_period, weights=None, run_num=-1, max_cycle_size=CYCLE_CAP, max_path_size=CHAIN_CAP, test_trial_num=None, trial_table=None, seed_num = None):
        self.random_state = np.random.RandomState()
        self.seed = seed_num
        self.test_trial_num = test_trial_num
        self.trial_table = trial_table
        self.population = Population(weights=weights)
        self.altruists = altruists
        self.per_period = per_period
        self.market = Market(self.population.generate_pairs(START_SIZE,first_flag=True), self.altruists, self.per_period, weights, run_num, max_cycle_size=max_cycle_size, max_path_size=max_path_size)
        self.cycle_chain_matches = [[0,0,0,0,0],[0],[0,0,0,0,0]]


    def run(self):
        """
        runs the simulations
        adds participants every matching period and adds altruists depending on settings
        """
        total_altruists = 0
        for i in range(NUM_PERIODS):
            print("Starting period " + str(i) + " - Trial number" + str(self.test_trial_num))
            num_pairs = np.random.poisson(ARRIVAL_RATE,None)
            new_pairs = self.population.generate_pairs(num_pairs, first_flag=False)
            altruists = list()
            if RANDOM_SAMPLE:
                num_altruists = self.random_state.poisson(self.altruists,None)
            else:
                num_altruists = self.altruists
            total_altruists += num_altruists
            x = np.random.randint(0,100,size=1)
            if i % self.per_period == 0:
                for j in range(num_altruists):
                    altruists.append(self.population.generate_altruist(self.random_state))
            y = np.random.randint(0, 100, size=1)
            cycle_path_lengths = self.market.run_period(new_participants=new_pairs,
                                   new_altruists=altruists, period_num=i, seed = self.seed, test_trial_num = self.test_trial_num, trial_table = self.trial_table)
            for i in range(0,5):
                self.cycle_chain_matches[0][i] += cycle_path_lengths[0][i]
                self.cycle_chain_matches[2][i] += cycle_path_lengths[2][i]
            self.cycle_chain_matches[1][0] += cycle_path_lengths[1][0]
        if self.trial_table is not None:
            self.trial_table.write(self.test_trial_num, 2, total_altruists)
            self.trial_table.write(self.test_trial_num, 32, self.cycle_chain_matches[0][0])
            self.trial_table.write(self.test_trial_num, 33, self.cycle_chain_matches[0][1])
            self.trial_table.write(self.test_trial_num, 34, self.cycle_chain_matches[0][2])
            self.trial_table.write(self.test_trial_num, 35, self.cycle_chain_matches[0][3])
            self.trial_table.write(self.test_trial_num, 36, self.cycle_chain_matches[0][4])
            self.trial_table.write(self.test_trial_num, 37, self.cycle_chain_matches[1][0])
            self.trial_table.write(self.test_trial_num, 38, self.cycle_chain_matches[2][0])
            self.trial_table.write(self.test_trial_num, 39, self.cycle_chain_matches[2][1])
            self.trial_table.write(self.test_trial_num, 40, self.cycle_chain_matches[2][2])
            self.trial_table.write(self.test_trial_num, 41, self.cycle_chain_matches[2][3])
            self.trial_table.write(self.test_trial_num, 42, self.cycle_chain_matches[2][4])

        self.market.metrics.close_table()


if __name__ == '__main__':
    #ta.test_altruists()
    tw.test_weights()
    #tcs.test_cycle_sizes()
