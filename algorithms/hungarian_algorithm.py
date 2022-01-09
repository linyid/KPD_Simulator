
"""
Implementation of the hungarian algorithms. Modified from https://gist.github.com/KartikTalwar/3158534
"""


def improve_labels(val):
    """
    change the labels, and maintain minSlack.
    """
    for u in S:
        lu[u] -= val
    for v in V:
        if v in T:
            lv[v] += val
        else:
            minSlack[v][0] -= val


def improve_matching(v):
    """
    apply the alternating path from v to the root in the tree.
    """
    u = T[v]
    if u in Mu:
        improve_matching(Mu[u])
    Mu[u] = v
    Mv[v] = u


def slack(u, v): return lu[u] + lv[v] - w[u][v]


def augment():
    """ augment the matching, possibly improving the labels on the way.
    """
    while True:
        # select edge (u,v) with u in S, v not in T and min slack
        ((val, u), v) = min([(minSlack[v], v) for v in V if v not in T])
        assert u in S
        if val > 0:
            improve_labels(val)
        # now we are sure that (u,v) is saturated
        assert slack(u, v) == 0
        T[v] = u  # add (u,v) to the tree
        if v in Mv:
            u1 = Mv[v]  # matched edge,
            assert not u1 in S
            S[u1] = True  # ... add endpoint to tree
            for v in V:  # maintain minSlack
                if not v in T and minSlack[v][0] > slack(u1, v):
                    minSlack[v] = [slack(u1, v), u1]
        else:
            improve_matching(v)  # v is a free vertex
            return


def max_weight_matching(weights):
    """ given w, the weight matrix of a complete bipartite graph,
        returns the mappings Mu : U->V ,Mv : V->U encoding the matching
        as well as the value of it.m
    """
    global U, V, S, T, Mu, Mv, lu, lv, minSlack, w
    w = weights
    n = len(w)
    U = V = range(n)
    lu = [max([w[u][v] for v in V]) for u in U]  # start with trivial labels
    lv = [0 for v in V]
    Mu = {}  # start with empty matching
    Mv = {}
    while len(Mu) < n:
        free = [u for u in V if u not in Mu]  # choose free vertex u0
        u0 = free[0]
        S = {u0: True}  # grow tree from u0 on
        T = {}
        minSlack = [[slack(u0, v), u0] for v in V]
        augment()
    # val. of matching is total edge weight
    val = sum(lu) + sum(lv)
    return (Mu, Mv, val)

