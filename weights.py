from config import LEARNING_RATE, ALT_WEIGHT
import numpy as np

class Weights:
    """
    Tracks and updates edge weights for simulations
    Weights are updated after each simulation and remain constant throughout a simulation
    ---------
    first_flag: boolean
        A flag that indicates whether or not it is the first time running a simulation
    w_cpra#: int
        The weight given to participants with has cpra#
        All weights are stored as an array
          O A B AB
        O
        A
        B
        AB
        Rows are recipient and column are donors (recipient, donor)
    ip_cpra#: float
        The initial proportion of participants with cpra#
    p_cpra#: float
        The proportion of participants with cpra# - updated throughout simulations
    """

    def __init__(self):

        self.first_flag = True

        self.w_cpra1 = [[1 for i in range(4)] for j in range(4)]
        self.w_cpra2 = [[1 for i in range(4)] for j in range(4)]
        self.w_cpra3 = [[1 for i in range(4)] for j in range(4)]
        self.w_cpra4 = [[1 for i in range(4)] for j in range(4)]
        self.w_cpra5 = [[1 for i in range(4)] for j in range(4)]

        # initial proportions
        # PER_CPRA = [0.14, 0.26, 0.08, 0.01, 0.51]

        self.ip_cpra1 = [[0.20 for i in range(4)] for j in range(4)]
        self.ip_cpra2 = [[0.20 for i in range(4)] for j in range(4)]
        self.ip_cpra3 = [[0.20 for i in range(4)] for j in range(4)]
        self.ip_cpra4 = [[0.20 for i in range(4)] for j in range(4)]
        self.ip_cpra5 = [[0.20 for i in range(4)] for j in range(4)]

        # proportion of each weight category

        self.p_cpra1 = [[0.20 for i in range(4)] for j in range(4)]
        self.p_cpra2 = [[0.20 for i in range(4)] for j in range(4)]
        self.p_cpra3 = [[0.20 for i in range(4)] for j in range(4)]
        self.p_cpra4 = [[0.20 for i in range(4)] for j in range(4)]
        self.p_cpra5 = [[0.20 for i in range(4)] for j in range(4)]


    def print_weights(self,file):
        print("The new weights are: CPRA1 " + str(self.w_cpra1) + " CPRA2 " + str(self.w_cpra2) + " CPRA3 " + str(self.w_cpra3) + " CPRA4 " + str(self.w_cpra4) + " CPRA5 " + str(self.w_cpra5),file=file)
        print()

    def print_proportions(self):
        print("The new proportions are: CPRA1 " + str(self.p_cpra1) + " CPRA2 " + str(self.p_cpra2) + " CPRA3 " + str(self.p_cpra3) + " CPRA4 " + str(self.p_cpra4) + " CPRA5 " + str(self.p_cpra5))

    def print_init_proportions(self):
        print("The new proportions are: CPRA1 " + str(self.ip_cpra1) + " CPRA2 " + str(self.ip_cpra2) + " CPRA3 " + str(
            self.ip_cpra3) + " CPRA4 " + str(self.ip_cpra4) + " CPRA5 " + str(self.ip_cpra5))

    def update_weights(self,file):
        # update rule
        f = lambda r: 10-9*np.exp(-r)
        for i in range(4):
            for j in range(4):
                if self.ip_cpra1[i][j] > 0:
                    self.w_cpra1[i][j] = round(f(self.p_cpra1[i][j] / self.ip_cpra1[i][j]),3)
                if self.ip_cpra2[i][j] > 0:
                    self.w_cpra2[i][j] = round(f(self.p_cpra2[i][j] / self.ip_cpra2[i][j]),3)
                if self.ip_cpra3[i][j] > 0:
                    self.w_cpra3[i][j] = round(f(self.p_cpra3[i][j] / self.ip_cpra3[i][j]),3)
                if self.ip_cpra4[i][j] > 0:
                    self.w_cpra4[i][j] = round(f(self.p_cpra4[i][j] / self.ip_cpra4[i][j]),3)
                if self.ip_cpra5[i][j] > 0:
                    self.w_cpra5[i][j] = round(f(self.p_cpra5[i][j] / self.ip_cpra5[i][j]),3)
        normalize = False
        if normalize:
            sum = np.sum(self.w_cpra1) + np.sum(self.w_cpra2)+ np.sum(self.w_cpra3)+ np.sum(self.w_cpra4)+ np.sum(self.w_cpra5)
            for i in range(4):
                for j in range(4):
                    self.w_cpra1[i][j] = 100 * self.w_cpra1[i][j] / sum
                    self.w_cpra2[i][j] = 100 * self.w_cpra2[i][j] / sum
                    self.w_cpra3[i][j] = 100 * self.w_cpra3[i][j] / sum
                    self.w_cpra4[i][j] = 100 * self.w_cpra4[i][j] / sum
                    self.w_cpra5[i][j] = 100 * self.w_cpra5[i][j] / sum

        self.print_weights(file)

    def update_weights1(self):
        for i in range(4):
            for j in range(4):
                if self.p_cpra1[i][j] > 0:
                    self.w_cpra1[i][j] = self.w_cpra1[i][j] + 2*(1 - (self.ip_cpra1[i][j] / self.p_cpra1[i][j]))
                if self.w_cpra1[i][j] < 2:
                    self.w_cpra1[i][j] = 2
                if self.p_cpra2[i][j] > 0:
                    self.w_cpra2[i][j] = self.w_cpra2[i][j] + 2*(1 - (self.ip_cpra2[i][j] / self.p_cpra2[i][j]))
                if self.w_cpra2[i][j] < 2:
                    self.w_cpra2[i][j] = 2
                if self.p_cpra3[i][j] > 0:
                    self.w_cpra3[i][j] = self.w_cpra3[i][j] + 2*(1 - (self.ip_cpra3[i][j] / self.p_cpra3[i][j]))
                if self.w_cpra3[i][j] < 2:
                    self.w_cpra3[i][j] = 2
                if self.p_cpra4[i][j] > 0:
                    self.w_cpra4[i][j] = self.w_cpra4[i][j] + 2*(1 - (self.ip_cpra4[i][j] / self.p_cpra4[i][j]))
                if self.w_cpra4[i][j] < 2:
                    self.w_cpra4[i][j] = 2
                if self.p_cpra5[i][j] > 0:
                    self.w_cpra5[i][j] = self.w_cpra5[i][j] + 2*(1 - (self.ip_cpra5[i][j] / self.p_cpra5[i][j]))
                if self.w_cpra5[i][j] <= 2:
                    self.w_cpra5[i][j] = 2
        self.print_weights()
        #normalize all the weight to 100
        normalize = False
        if normalize:
            sum = 0
            sum = sum + np.sum(self.w_cpra1)
            sum = sum + np.sum(self.w_cpra2)
            sum = sum + np.sum(self.w_cpra3)
            sum = sum + np.sum(self.w_cpra4)
            sum = sum + np.sum(self.w_cpra5)
            for i in range(4):
                for j in range(4):
                    self.w_cpra1[i][j] = 100 * self.w_cpra1[i][j] / sum
                    self.w_cpra2[i][j] = 100 * self.w_cpra2[i][j] / sum
                    self.w_cpra3[i][j] = 100 * self.w_cpra3[i][j] / sum
                    self.w_cpra4[i][j] = 100 * self.w_cpra4[i][j] / sum
                    self.w_cpra5[i][j] = 100 * self.w_cpra5[i][j] / sum
            self.print_weights()

    def set_init_proportions(self, pop_size, p1, p2, p3, p4, p5):
        for i in range(4):
            for j in range(4):
                self.ip_cpra1[i][j] = p1[i][j]/pop_size
                self.ip_cpra2[i][j] = p2[i][j]/pop_size
                self.ip_cpra3[i][j] = p3[i][j]/pop_size
                self.ip_cpra4[i][j] = p4[i][j]/pop_size
                self.ip_cpra5[i][j] = p5[i][j]/pop_size
        self.first_flag = False

    def update_proportions(self, pop_size, p1, p2, p3, p4, p5):
        for i in range(4):
            for j in range(4):
                self.p_cpra1[i][j] = p1[i][j]/pop_size
                self.p_cpra2[i][j] = p2[i][j]/pop_size
                self.p_cpra3[i][j] = p3[i][j]/pop_size
                self.p_cpra4[i][j] = p4[i][j]/pop_size
                self.p_cpra5[i][j] = p5[i][j]/pop_size

    def reset_flag(self):
        self.first_flag = True
