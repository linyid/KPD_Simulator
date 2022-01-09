import simulations as s
"""
Has all the functionalities for running tests on the affects of altruists in the market
"""


def test_cycle_sizes():
    # print("Starting Simulations with 0 altruists")
    # sim = Simulations(altruists=0, per_period=1)
    # sim.run()
    for i in [2, 3, 4]:
        print("Starting Simulations with " + str(i) + " cycles ")
        sim = s.Simulations(altruists=5, per_period=1, max_cycle_size=i)
        sim.run()


if __name__ == '__main__':
    test_cycle_sizes()
