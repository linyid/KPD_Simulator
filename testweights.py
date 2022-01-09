from weights import Weights
import simulations as s
from config import NUM_ALTRUISTS, RESULTS_PATH
import os
import numpy as np
"""
This is for training weights for OPT 
Run with 'OPT' set in the config file
"""


def test_weights():
    np.random.seed()

    file_path = os.path.join(RESULTS_PATH, "weights.txt")
    f = open(file_path, "a")

    w = Weights()
    run_num = 1
    for i in [NUM_ALTRUISTS]:
        for j in range(50):
            cycle_matches = 0
            chain_matches = 0
            print("Starting Simulations with mean of " + str(i) + " altruists every period")
            sim = s.Simulations(altruists=i, per_period=1, weights=w, run_num=run_num)
            sim.run()
            w.update_weights(f)
            w.reset_flag()
            run_num = run_num + 1
            cycle_matches += sim.cycle_chain_matches[0]
            chain_matches += sim.cycle_chain_matches[1]
            print("There are " + (str(cycle_matches) + str(chain_matches)) + " matches")
            print("Chain match proportion is {}".format(chain_matches / (cycle_matches + chain_matches)))
    f.close()




if __name__ == '__main__':
    test_weights()