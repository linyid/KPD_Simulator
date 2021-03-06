"""
author: Margarida Carvalho (adapted from Joao Pedro Pedroso code)
License: MIT
Python 3
REQUIREMENTS: GUROBI
This code determines a solution that maximizes the number of transplants given a directed graph
where cycles of length at most K are allowed and chains of length at most L are allowed.
"""
# READ INSTANCE
# INPUT
# filename - it is a string
# OUTPUT
# G - it is a incidence list; a dictionary
# num_V - number of nodes
# Nb_arcs - number of arcs
# altruistic_list - list of altruistic nodes
def read_kep(filename):
    #read file in the 'standard' kep format
    f = open(filename)
    num_V, num_E = map(int,f.readline().split()) # number of nodes, number of edges
    # nodes are labeled from 0 to n
    G = {i:[] for i in range(num_V)}
    Nb_arcs = 0
    for _ in range(num_E):
        v1, v2, w = map(int,f.readline().split()) # there is an arc v1 to v2; ARC's weights are being ignored (i.e., they are 1)
        G[v1].append(v2)
        Nb_arcs = Nb_arcs +1
    num_Altruistic = int(eval(f.readline())) # number of altruistic donors
    altruistic_list = []
    for _ in range(num_Altruistic):
        altruistic_list.append(int(eval(f.readline())))
    return G, num_V, Nb_arcs, altruistic_list


# Compute all the cycles c of length less or equal to K and save the respective length wc
# make cycles to start in the node with smallest label
def normalize(cycle):
    cmin = min(cycle)
    while cycle[0] != cmin:
        v = cycle.pop(0)
        cycle.append(v)

def all_cycles(cycles, path, node, tovisit, adj,K):
    global spc
    for i in adj[node]:
        if i in path:
            j = path.index(i)
            cycle = path[j:]+[node]
            normalize(cycle)
            cycles.add(tuple(cycle))
        if i in tovisit:
            if K-1 > 0:
                all_cycles(cycles,path+[node],i,tovisit-set([i]),adj,K-1)
    # spc = spc[:-4]
    return cycles


# INPUT
# adj - incidence list; a dictionary
# K - maximumsize for cycles length
# OUTPUT
# cycles - set of tuples of size K
def get_all_cycles(adj,K):
    tovisit = set(adj.keys())
    visited = set([])
    cycles = set([])
    for i in tovisit:
        tmpvisit = set(tovisit)
        tmpvisit.remove(i)
        first = i
        all_cycles(cycles,[],first,tmpvisit,adj,K)
    return cycles

from gurobipy import *
# INPUT
# G - incidence list; a dictionary
# K - maximum size for cycles length
# L - maximum length of chain size for cycles length
# altruistic_list - list of altruistic nodes
# OUTPUT
# Optimal value
# running time (seconds)
# model
# variables X
# variables Z
def solve_KEP(G,K,L=0,altruistic_list=[]):
    setParam("OutputFlag",0)
    # compute all cycles of length at most 3
    Cycles_k = list(get_all_cycles(G,K))
    # create model
    m = Model("Deterministic KEP")
    # create the variables associated with cycles
    X = {i+1: m.addVar(obj = len(c), vtype="B",name="X"+str(i+1)) for i,c in enumerate(Cycles_k)}
    m.update()
    # to understand the dictionary below see how chains can be considered in "Position-Indexed Formulations for Kidney Exchange"
    K_dic = {(i,j):[1] if i in altruistic_list else range(2,L+1) for i in G.keys() for j in G[i]}
    # create variables for chains
    Z = {(i,j,l): m.addVar(obj = 1, vtype="B",name="z"+str(i)+"_"+str(j)+"_"+str(l)) for i,j in K_dic.keys() for l in K_dic[(i,j)]}
    m.update()
    for v in G.keys():
        # WRONG constraint each vertex donates at most one kidney: not enough for correctness!
        #m.addConstr(quicksum(X[i+1]  for i,c in enumerate(Cycles_k) if v in c)+quicksum(Z[(v,j,l)] for j in G[v] for l in K_dic[(v,j)])<= 1)
        # each vertex receives at most one kidney: correct!
        m.addConstr(quicksum(X[i+1]  for i,c in enumerate(Cycles_k) if v in c)+quicksum(Z[(j,v,l)] for j in G.keys() if v in G[j] for l in K_dic[(j,v)])<= 1)
        m.update()
        if v not in altruistic_list:
            for l in range(1,L):
                m.addConstr(quicksum(Z[(j,v,l)] for j in G.keys() if v in G[j] and l in K_dic[(j,v)])>= quicksum(Z[(v,j,l+1)] for j in G[v]))
                m.update()
        else:
            m.addConstr(quicksum(Z[(v,j,1)] for j in G[v])<= 1)
            m.update()
    m.ModelSense = -1 # maximize
    m.update()
    m.optimize(gap_root)
    print("\n###############################################")
    print("# Optimal solution for KEP #")
    print("###############################################")
    Len_cycles = []
    for i,c in enumerate(Cycles_k):
        if X[i+1].x>0.5: # that is, X[i+1]= 1; OBS: I use this 0.5 because it might happen that python sees X[i+1]=1.0 different from 1
            print(" cycle ", c)
            Len_cycles.append(len(c))
    for v in altruistic_list:
        aux_chain = []
        aux_v = v
        while sum(Z[(aux_v,j,k)].x for j in G[aux_v] for k in K_dic[(aux_v,j)])>0.5:
            for j in G[aux_v]:
                for k in K_dic[(aux_v,j)]:
                    if Z[(aux_v,j,k)].x>0.5:
                        aux_chain.append((aux_v,j))
                        aux_v = j
                        break
                    else:
                        continue
                break
        if aux_chain !=[]:
            print(" chain ", aux_chain)
    print("\n OPT = ",m.ObjVal,"  time = ",m.Runtime)
    return m.ObjVal,m.Runtime, m, X, Z

def gap_root(m,where):
    if where == GRB.callback.MIP: # current node being explored
        if m.cbGet(GRB.Callback.MIP_NODCNT) == 0: # root node
             root_best = m.cbGet(GRB.Callback.MIP_OBJBST)
             root_bound = m.cbGet(GRB.Callback.MIP_OBJBND)
             print("GAP ", ((root_bound-root_best)/root_bound)*100)
             

if __name__ == "__main__":
    # Example 1
    # read graph from file
    G, num_V, Nb_arcs, altruistic_list = read_kep("example1.txt")
    # find the maximum number of transplants, i.e., solve KEP
    OPT, cpu_time,_,_,_ = solve_KEP(G,3,3,altruistic_list)
