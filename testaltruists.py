import time
import simulations as s
from config import NUM_ALTRUISTS, RESULTS_PATH, CYCLE_CAP, CHAIN_CAP, ALGORITHM, NUM_ALTRUISTS, WEIGHTS
import numpy as np
import xlsxwriter
import os

"""
Has all the functionalities for running tests on the affects of altruists in the market
"""


def test_altruists(seed=None, test_trial_num=None, trial_table=None):
    np.random.seed(seed)
    cycle_matches = 0
    chain_matches = 0
    tic = time.perf_counter()
    for i in [NUM_ALTRUISTS]:
        for j in [1]:
            print("Starting Simulations with " + str(i) + " altruists every " + str(j) + " periods")
            sim = s.Simulations(altruists=i, per_period=j, test_trial_num=test_trial_num, trial_table=trial_table,
                                seed_num=seed)
            sim.run()
            for i in range(0,4):
                cycle_matches += sim.cycle_chain_matches[0][i]*(i+2)
            chain_matches += sim.cycle_chain_matches[1][0]
    toc = time.perf_counter()
    print("The simulation finishes with %s second" % str(toc - tic))
    print("There are " + str(cycle_matches) + " cycle matches and " + str(chain_matches) + " chain matches")
    print("Chain match proportion is {}".format(chain_matches / (cycle_matches + chain_matches)))
    print("---------------------------------------------------------")


# TEST_SEED = True
def test_altruists_with_seeds():
    '''
    run test_altruists multiple times with different seeds
    :return:
    '''
    #seeds = [81]
    #'''
    seeds = [581,  81, 273,  86,  64, 754, 662,   7, 916, 128, 870, 315, 394,
       317,  30, 767, 687, 256, 501, 526, 177, 784, 520, 948, 164, 822,
       913, 895, 537, 171, 254, 552, 297, 822, 288, 445, 247, 618, 327,
       342, 224, 571, 516, 792, 284, 925, 105, 676, 638, 200]
    #'''
    results_file_path = os.path.join(RESULTS_PATH, "SeedTest_" + str(len(seeds)) + "_" + WEIGHTS + str(NUM_ALTRUISTS) +
            "AltruistsPer" + str(1) + "Periods_" + str(CYCLE_CAP) + "_" + str(CHAIN_CAP) + "_min_150" + ".xlsx")
    workbook = xlsxwriter.Workbook(results_file_path)
    trial_table = workbook.add_worksheet()
    # random_state = np.random.RandomState()

    test_trial_num = 1
    for seed in seeds:
        test_altruists(seed, test_trial_num, trial_table)
        test_trial_num += 1
    workbook.close()


if __name__ == '__main__':
    #test_altruists(307)
    test_altruists_with_seeds()
