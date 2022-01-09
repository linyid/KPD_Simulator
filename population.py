from participant import Participant
import os
from config import PER_A, PER_B, PER_AB, PER_O, PER_CPRA, CPRA, TIME_TO_CRITICAL_LOW, ALT_WEIGHT, ARRIVAL_RATE, WEIGHTS, DATA_PATH, PER_BC, PER_AL, PER_SK, PER_MN, PER_ON, PER_QC, PER_NS, PER_NB, PER_PEI, PER_NFL
from config import CPRA1, CPRA2, CPRA3, CPRA4, CPRA5
import numpy as np


class Population:
    """
    A population where pairs are selected from
    ---------
    count: int
        count that keeps track of how many pairs have entered the market and ensures that each pair is given a unique id
    """

    def __init__(self, weights=None):
        #self.random_state = np.random.RandomState()
        self.count = 0
        dialysis_days_file_path = os.path.join(DATA_PATH, "patient_days_bootstring.npy")
        donor_ages_file_path = os.path.join(DATA_PATH, "donor_ages_bootstring.npy")
        patient_ages_file_path = os.path.join(DATA_PATH, "patient_ages_bootstring.npy")

        self.dialysis_days = np.load(dialysis_days_file_path)
        self.donor_ages = np.load(donor_ages_file_path)
        self.patient_ages = np.load(patient_ages_file_path)

        self.weights = weights



    def generate_pairs(self, num_pairs,first_flag):
        """
        generates new patient-donor pairs based on the distribution of the population
        :param num_pairs: int - the number of pairs to generate
               first_flag: boolean - a boolean indicating the first period
        :return: a list of tuples of participants in the form (recipient, donor)
        """
        new_pairs = list()
        i = 0
        while i < num_pairs:
            index = np.random.choice(len(CPRA), p=PER_CPRA)
            cpra_range = CPRA[index]
            cpra = np.random.uniform(cpra_range[0], cpra_range[1])
            donor_type = np.random.choice(['A', 'B', 'O', 'AB'], p=[PER_A, PER_B, PER_O, PER_AB])
            recipient_type = np.random.choice(['A', 'B', 'O', 'AB'], p=[PER_A, PER_B, PER_O, PER_AB])
            weight = self.calculate_weight(donor_type, recipient_type, cpra, index)

            dialysis_day = np.random.choice(self.dialysis_days)
            donor_age = np.random.choice(self.donor_ages)
            patient_age = np.random.choice(self.patient_ages)

            # generate a random time_to_critical value using a uniform distribution
            if first_flag:
                upper = 70
                lower = 10
                time_to_critical = int(np.random.uniform(low = lower, high = upper, size = 1))
            else:
                #a = 1
                time_to_critical = int(np.random.poisson(TIME_TO_CRITICAL_LOW, size = 1))

            province = np.random.choice(['BC', 'AL', 'SK', 'MN', 'ON', 'QC', 'NS', 'NB', 'PEI', 'NFL'], p=[PER_BC, PER_AL, PER_SK, PER_MN, PER_ON, PER_QC, PER_NS, PER_NB, PER_PEI, PER_NFL])

            # if they are blood type compatible, only create new participant pairs if they are tissue type incompatible
            if donor_type == 'O' or recipient_type == 'AB' or donor_type == recipient_type:
                if np.random.choice([True, False], p=[cpra, 1-cpra]):
                    donor = Participant(self.count, donor_type, donor=True, recipient=False, altruist = False, time_to_critical=time_to_critical, weight=weight, cpra=cpra, age=donor_age, dialysis_days=dialysis_day, province=province)
                    recipient = Participant(self.count, recipient_type, donor=False, recipient=True, altruist = False, time_to_critical=time_to_critical, weight=weight, cpra=cpra, age=patient_age, dialysis_days=dialysis_day, province=province)
                    new_pairs.append((recipient, donor))
                    i += 1
                    self.count += 1
            else:
                donor = Participant(self.count, donor_type, donor=True, recipient=False, altruist = False, time_to_critical=time_to_critical, weight=weight, cpra=cpra, age=donor_age, dialysis_days=dialysis_day, province=province)
                recipient = Participant(self.count, recipient_type, donor=False, recipient=True, altruist = False, time_to_critical=time_to_critical, weight=weight, cpra=cpra, age=patient_age, dialysis_days=dialysis_day,province=province)
                new_pairs.append((recipient, donor))
                i += 1
                self.count += 1
        return new_pairs

    def gen_rand_population_size(self):
        """
        gets a random population size centered around the arrival rate
        :return: integer representing a population size
        """
        difference = int(float(ARRIVAL_RATE) / 3.0)
        return np.random.choice([ARRIVAL_RATE - (difference * 2), ARRIVAL_RATE - difference, ARRIVAL_RATE, ARRIVAL_RATE + difference, ARRIVAL_RATE + (difference * 2)], p=[0.1, 0.2, 0.4, 0.2, 0.1])

    def generate_altruist(self, random_state):
        """
        generates an altruistic donor
        :return: a tuple of Participants in the form ("fake recipient", altruisitc donor)
        """
        donor_age = random_state.choice(self.donor_ages)
        donor_type = random_state.choice(['A', 'B', 'O', 'AB'], p=[PER_A, PER_B, PER_O, PER_AB])
        time_to_critical = int(random_state.poisson(lam = TIME_TO_CRITICAL_LOW, size = 1))
        altruistic_donor = Participant(self.count, donor_type, donor=True, recipient=False, altruist = True, time_to_critical=time_to_critical, weight=ALT_WEIGHT, cpra=0, age=donor_age, dialysis_days=0)
        recipient = Participant(self.count, blood_type='X', donor=False, recipient=True,  altruist = True, time_to_critical=time_to_critical, weight=ALT_WEIGHT, cpra=0, dialysis_days=0)
        self.count += 1
        return recipient, altruistic_donor

    def calculate_weight(self, donor_type, recipient_type, cpra, index):
        """
        determines the weight of a pair based on blood type of patient and donor and cpra
        :param donor_type: blood type of the donor
        :param recipient_type: blood type of the recipient
        :param cpra: the cpra
        :return: a weight in the form of an int
        """
        if WEIGHTS == "CONST":
            return 2
        elif WEIGHTS == "OPT":
            # weights obtained while training
            if self.weights is not None:
                if cpra == CPRA[0][1]:
                    if donor_type == 'O':
                        if recipient_type == 'O':
                            return self.weights.w_cpra1[0][0]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra1[1][0]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra1[2][0]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra1[3][0]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra1[4][0]
                    if donor_type == 'A':
                        if recipient_type == 'O':
                            return self.weights.w_cpra1[0][1]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra1[1][1]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra1[2][1]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra1[3][1]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra1[4][1]
                    if donor_type == 'B':
                        if recipient_type == 'O':
                            return self.weights.w_cpra1[0][2]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra1[1][2]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra1[2][2]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra1[3][2]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra1[4][2]
                    if donor_type == 'AB':
                        if recipient_type == 'O':
                            return self.weights.w_cpra1[0][3]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra1[1][3]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra1[2][3]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra1[3][3]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra1[4][3]
                elif cpra <= CPRA[1][1]:
                    if donor_type == 'O':
                        if recipient_type == 'O':
                            return self.weights.w_cpra2[0][0]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra2[1][0]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra2[2][0]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra2[3][0]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra2[4][0]
                    if donor_type == 'A':
                        if recipient_type == 'O':
                            return self.weights.w_cpra2[0][1]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra2[1][1]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra2[2][1]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra2[3][1]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra2[4][1]
                    if donor_type == 'B':
                        if recipient_type == 'O':
                            return self.weights.w_cpra2[0][2]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra2[1][2]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra2[2][2]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra2[3][2]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra2[4][2]
                    if donor_type == 'AB':
                        if recipient_type == 'O':
                            return self.weights.w_cpra2[0][3]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra2[1][3]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra2[2][3]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra2[3][3]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra2[4][3]
                elif cpra <= CPRA[2][1]:
                    if donor_type == 'O':
                        if recipient_type == 'O':
                            return self.weights.w_cpra3[0][0]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra3[1][0]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra3[2][0]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra3[3][0]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra3[4][0]
                    if donor_type == 'A':
                        if recipient_type == 'O':
                            return self.weights.w_cpra3[0][1]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra3[1][1]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra3[2][1]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra3[3][1]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra3[4][1]
                    if donor_type == 'B':
                        if recipient_type == 'O':
                            return self.weights.w_cpra3[0][2]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra3[1][2]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra3[2][2]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra3[3][2]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra3[4][2]
                    if donor_type == 'AB':
                        if recipient_type == 'O':
                            return self.weights.w_cpra3[0][3]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra3[1][3]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra3[2][3]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra3[3][3]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra3[4][3]
                elif cpra <= CPRA[3][1]:
                    if donor_type == 'O':
                        if recipient_type == 'O':
                            return self.weights.w_cpra4[0][0]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra4[1][0]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra4[2][0]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra4[3][0]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra4[4][0]
                    if donor_type == 'A':
                        if recipient_type == 'O':
                            return self.weights.w_cpra4[0][1]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra4[1][1]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra4[2][1]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra4[3][1]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra4[4][1]
                    if donor_type == 'B':
                        if recipient_type == 'O':
                            return self.weights.w_cpra4[0][2]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra4[1][2]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra4[2][2]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra4[3][2]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra4[4][2]
                    if donor_type == 'AB':
                        if recipient_type == 'O':
                            return self.weights.w_cpra4[0][3]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra4[1][3]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra4[2][3]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra4[3][3]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra4[4][3]
                elif cpra <= CPRA[4][1]:
                    if donor_type == 'O':
                        if recipient_type == 'O':
                            return self.weights.w_cpra5[0][0]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra5[1][0]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra5[2][0]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra5[3][0]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra5[4][0]
                    if donor_type == 'A':
                        if recipient_type == 'O':
                            return self.weights.w_cpra5[0][1]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra5[1][1]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra5[2][1]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra5[3][1]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra5[4][1]
                    if donor_type == 'B':
                        if recipient_type == 'O':
                            return self.weights.w_cpra5[0][2]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra5[1][2]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra5[2][2]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra5[3][2]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra5[4][2]
                    if donor_type == 'AB':
                        if recipient_type == 'O':
                            return self.weights.w_cpra5[0][3]
                        elif recipient_type == 'A':
                            return self.weights.w_cpra5[1][3]
                        elif recipient_type == 'B':
                            return self.weights.w_cpra5[2][3]
                        elif recipient_type == 'AB':
                            return self.weights.w_cpra5[3][3]
                        elif recipient_type == 'X':
                            return self.weights.w_cpra5[4][3]
            else:
                # specify the weights you want here - usually use those found by training
                # initialize 5 cpra matrices
                # select the weights according to the input, search by cpra first
                if index == 0:
                    if recipient_type == "O":
                        if donor_type == "O":
                            return CPRA1[0][0]
                        elif donor_type == "A":
                            return CPRA1[0][1]
                        elif donor_type == "B":
                            return CPRA1[0][2]
                        elif donor_type == "AB":
                            return CPRA1[0][3]
                    if recipient_type == "A":
                        if donor_type == "O":
                            return CPRA1[1][0]
                        elif donor_type == "A":
                            return CPRA1[1][1]
                        elif donor_type == "B":
                            return CPRA1[1][2]
                        elif donor_type == "AB":
                            return CPRA1[1][3]
                    if recipient_type == "B":
                        if donor_type == "O":
                            return CPRA1[2][0]
                        elif donor_type == "A":
                            return CPRA1[2][1]
                        elif donor_type == "B":
                            return CPRA1[2][2]
                        elif donor_type == "AB":
                            return CPRA1[2][3]
                    if recipient_type == "AB":
                        if donor_type == "O":
                            return CPRA1[3][0]
                        elif donor_type == "A":
                            return CPRA1[3][1]
                        elif donor_type == "B":
                            return CPRA1[3][2]
                        elif donor_type == "AB":
                            return CPRA1[3][3]
                elif index == 1:
                    if recipient_type == "O":
                        if donor_type == "O":
                            return CPRA2[0][0]
                        elif donor_type == "A":
                            return CPRA2[0][1]
                        elif donor_type == "B":
                            return CPRA2[0][2]
                        elif donor_type == "AB":
                            return CPRA2[0][3]
                    if recipient_type == "A":
                        if donor_type == "O":
                            return CPRA2[1][0]
                        elif donor_type == "A":
                            return CPRA2[1][1]
                        elif donor_type == "B":
                            return CPRA2[1][2]
                        elif donor_type == "AB":
                            return CPRA2[1][3]
                    if recipient_type == "B":
                        if donor_type == "O":
                            return CPRA2[2][0]
                        elif donor_type == "A":
                            return CPRA2[2][1]
                        elif donor_type == "B":
                            return CPRA2[2][2]
                        elif donor_type == "AB":
                            return CPRA2[2][3]
                    if recipient_type == "AB":
                        if donor_type == "O":
                            return CPRA2[3][0]
                        elif donor_type == "A":
                            return CPRA2[3][1]
                        elif donor_type == "B":
                            return CPRA2[3][2]
                        elif donor_type == "AB":
                            return CPRA2[3][3]
                elif index == 2:
                    if recipient_type == "O":
                        if donor_type == "O":
                            return CPRA3[0][0]
                        elif donor_type == "A":
                            return CPRA3[0][1]
                        elif donor_type == "B":
                            return CPRA3[0][2]
                        elif donor_type == "AB":
                            return CPRA3[0][3]
                    if recipient_type == "A":
                        if donor_type == "O":
                            return CPRA3[1][0]
                        elif donor_type == "A":
                            return CPRA3[1][1]
                        elif donor_type == "B":
                            return CPRA3[1][2]
                        elif donor_type == "AB":
                            return CPRA3[1][3]
                    if recipient_type == "B":
                        if donor_type == "O":
                            return CPRA3[2][0]
                        elif donor_type == "A":
                            return CPRA3[2][1]
                        elif donor_type == "B":
                            return CPRA3[2][2]
                        elif donor_type == "AB":
                            return CPRA3[2][3]
                    if recipient_type == "AB":
                        if donor_type == "O":
                            return CPRA3[3][0]
                        elif donor_type == "A":
                            return CPRA3[3][1]
                        elif donor_type == "B":
                            return CPRA3[3][2]
                        elif donor_type == "AB":
                            return CPRA3[3][3]
                elif index == 3:
                    if recipient_type == "O":
                        if donor_type == "O":
                            return CPRA4[0][0]
                        elif donor_type == "A":
                            return CPRA4[0][1]
                        elif donor_type == "B":
                            return CPRA4[0][2]
                        elif donor_type == "AB":
                            return CPRA4[0][3]
                    if recipient_type == "A":
                        if donor_type == "O":
                            return CPRA4[1][0]
                        elif donor_type == "A":
                            return CPRA4[1][1]
                        elif donor_type == "B":
                            return CPRA4[1][2]
                        elif donor_type == "AB":
                            return CPRA4[1][3]
                    if recipient_type == "B":
                        if donor_type == "O":
                            return CPRA4[2][0]
                        elif donor_type == "A":
                            return CPRA4[2][1]
                        elif donor_type == "B":
                            return CPRA4[2][2]
                        elif donor_type == "AB":
                            return CPRA4[2][3]
                    if recipient_type == "AB":
                        if donor_type == "O":
                            return CPRA4[3][0]
                        elif donor_type == "A":
                            return CPRA4[3][1]
                        elif donor_type == "B":
                            return CPRA4[3][2]
                        elif donor_type == "AB":
                            return CPRA4[3][3]
                elif index == 4:
                    if recipient_type == "O":
                        if donor_type == "O":
                            return CPRA5[0][0]
                        elif donor_type == "A":
                            return CPRA5[0][1]
                        elif donor_type == "B":
                            return CPRA5[0][2]
                        elif donor_type == "AB":
                            return CPRA5[0][3]
                    if recipient_type == "A":
                        if donor_type == "O":
                            return CPRA5[1][0]
                        elif donor_type == "A":
                            return CPRA5[1][1]
                        elif donor_type == "B":
                            return CPRA5[1][2]
                        elif donor_type == "AB":
                            return CPRA5[1][3]
                    if recipient_type == "B":
                        if donor_type == "O":
                            return CPRA5[2][0]
                        elif donor_type == "A":
                            return CPRA5[2][1]
                        elif donor_type == "B":
                            return CPRA5[2][2]
                        elif donor_type == "AB":
                            return CPRA5[2][3]
                    if recipient_type == "AB":
                        if donor_type == "O":
                            return CPRA5[3][0]
                        elif donor_type == "A":
                            return CPRA5[3][1]
                        elif donor_type == "B":
                            return CPRA5[3][2]
                        elif donor_type == "AB":
                            return CPRA5[3][3]
                return 2
        return 2

