import numpy as np
import numpy.random as rnd
import scipy.stats as sc
import matplotlib.pyplot as plt
import seaborn as sns

nodes = 10
payments = [2,5,4,2,6,3,1,7,4,5]
journey_len = np.array([2,5,4,2,6,3,1,7,4,5])
rnd.shuffle(journey_len)
distance = [[rnd.random()]*nodes]*nodes
import copy 


weight_p = 100
weights = np.array([[weight_p]*nodes]*nodes) - np.eye(10)*weight_p
weights_aux = copy.deepcopy(weights)



modes = {
    "greedy":None,
    "uniform":np.array([[weight_p]*nodes]*nodes) - np.eye(nodes)*weight_p,
}

def init_weights(mode):
    return modes[mode]


def run_generations(ant_count, payments, init_mode = "uniform", iterations=50, bound=np.inf):
    weights = init_weights(init_mode)
    for _ in range(iterations):
        weights = run_colony(ant_count, weights, bound, payments)
    
    return weights

def run_colony(ant_count, weights, bound, payments):
    total_payments = np.sum(payments)
    weights_aux = copy.deepcopy(weights)
    for _ in range(ant_count):

        ant_hist, ant_earned = run_ant(weights,bound,payments)
        feromone = ant_earned / total_payments

        for j in range(len(ant_hist)-1):
            weights_aux[ant_hist[j]][ant_hist[j+1]] += feromone

    return weights_aux


def run_ant(weights,bound,payments):
    ant_hist = []
    ant_travelled = 0
    ant_earned = 0
    ant_now = rnd.randint(0,nodes)
    while (ant_travelled+journey_len[ant_now]<=bound):
        ant_travelled += journey_len[ant_now]
        ant_earned += payments[ant_now]
        ant_hist += [ant_now]

        available_next = [n for n in range(nodes) if n not in ant_hist]
        if (len(available_next)==0):
            break

        p = weights[ant_now][available_next]
        p /= np.sum(p)
        ant_next = rnd.choice(available_next, p = p)
        ant_travelled += distance[ant_now][ant_next]

                        
        ant_now = ant_next

    
    
    return ant_hist, ant_earned





