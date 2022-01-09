

### POPULATION DISTRIBUTION ###

# percentage of the population with blood type A
PER_A = 0.42
# percentage of the population with blood type B
PER_B = 0.09
# percentage of the population with blood type AB
PER_AB = 0.03
# percentage of the population with blood type O
PER_O = 0.46

# percertage with each CPRA level  change this!!!!!
PER_CPRA = [0.24, 0.29, 0.24, 0.1, 0.13]
# CPRA levels - note: these represent
CPRA = [(0, 0), (0.01, 0.50), (0.51, 0.94), (0.95, 0.96), (0.97, 1)]

#percentage in each province

#includes Yukon
PER_BC = 0.2508833922261484

PER_AL = 0.11749116607773852
PER_SK = 0.028268551236749116
PER_MN = 0.046819787985865724
PER_ON = 0.37809187279151946
PER_QC = 0.10865724381625441
PER_NS = 0.026501766784452298
PER_NB = 0.023851590106007067
PER_PEI = 0.0035335689045936395
PER_NFL = 0.015901060070671377


# the edge weight to given to altruistic donors - NOTE this cannot be 0
ALT_WEIGHT = -150

# boolean indicating whether or not to take in account perishing
PERISH = False
# on average, the amount of time a patient stays in the market
TIME_TO_CRITICAL_LOW = 70

### FILE I/O ###

RESULTS_PATH = "Results/FinalTests"
DATA_PATH = "data"

### SIMULATION CONFIGURATIONS ###

# enable or disable random sample of population, particularly for the number of altruist per period
RANDOM_SAMPLE = True

#kpd arrival rate is 37
ARRIVAL_RATE = 37
#kpd start size is 100
START_SIZE = 150

# length of a period of a matching cycle (in months)
# kpd period length is 4 months
PERIOD_LENGTH = 4
# standard number of matching periods is 100
NUM_PERIODS = 50

# number of altruists per period. If use random sample, the mean is 4.562
NUM_ALTRUISTS = 4.562

# maximum cycle and chain size
# when using large chain size, set 'ALGORITHM' to be 'FAST' or 'LP'
CYCLE_CAP = 5
CHAIN_CAP = 5

# the probability that that last unused donor of a chain is willing
# to be an altruist in the future
REUSE_RATE = 0

# the learning rate of weight learning
LEARNING_RATE = 0.5


# matching algorithm used
# either 'HA' for hungarian algorithm (doesn't restrict cycle size) or 'LP' for linear program or 'FAST' for LP with faster cycle selection
# make sure that weights used are integer if you run with "HA"
ALGORITHM = "FAST"

# edge weights used
# either 'KPD' for the current Canadian KPD weights, 'OPT' for the optimized weights, or when training optimized weights, 'CONST' for constant weights
WEIGHTS = "KPD"

# An indicator for printing the ip solver characters
PRINT = False


# Learned weights here
# Current weight is learnt by the update rule f(r) = 4-3exp(-r)
CPRA1 = [[1, 3.327, 1.185, 1.0], [1, 1, 1.0, 1.0], [1, 1.521, 1, 1.0], [1, 1, 1, 1]]
CPRA2 = [[1.521, 1.746, 1.521, 1.521], [1.0, 1.0, 1.0, 1.521], [1.0, 2.223, 1.0, 1.0], [1.0, 1.0, 1.0, 1]]
CPRA3 = [[1.22, 1.673, 3.828, 3.891], [1.673, 1.0, 1.273, 1.0], [1.0, 2.307, 1.0, 1.0], [1.0, 1.0, 1, 1.0]]
CPRA4 = [[1.951, 3.481, 2.844, 3.113], [1.125, 1.273, 1.0, 1.0], [1.0, 1.51, 1.0, 1.0], [1.0, 1.368, 1, 1.0]]
CPRA5 = [[2.241, 3.817, 3.51, 3.316], [1.0, 3.044, 1.884, 1.469], [2.507, 2.137, 1.0, 1.0], [1.4, 1.0, 1.0, 1.0]]






