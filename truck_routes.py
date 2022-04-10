
import numpy as np
import string
import itertools

from torch import combinations
from antcolony import ant_colony


routes_id = list(string.ascii_uppercase)[:10]
pickup_coordinates = [(15,41),(32,20),(25,73),(35,53),(74,38),(43,52),(32,86),(11,39),(28,1),(26,82)]
dropoff_coordinates = [(85,66),(94,70),(64,75),(8,53),(68,19),(79,0),(12,53),(36,38),(64,87),(40,4)]
earnings = [77,92,44,37,38,83,51,39,102,96]


class RouteOptimizer:
    def __init__(self, routes_id, pickup_coordinates, dropoff_coordinates, earnings, start_pos = (50,50), bound=np.inf) -> None:
        self.routes_id = routes_id 
        self.pickup_coordinates = pickup_coordinates 
        self.dropoff_coordinates = dropoff_coordinates
        self.earnings = earnings
        self.start_pos = start_pos
        self.bound = bound

        self.routes = self.generate_routes()
        self.job_combinations = self.generate_all_job_combinations()

    def generate_routes(self):
        routes = {}

        for id, pu_c, do_c, earns in zip(self.routes_id,self.pickup_coordinates,self.dropoff_coordinates,self.earnings):
            pu_cc = np.array(pu_c)
            do_cc = np.array(do_c)
            routes[id] = {
                "routeId":id,
                "data":{
                    "pickup":pu_cc,
                    "dropoff":do_cc,
                    "distance":np.linalg.norm(pu_cc-do_cc),
                    "earnings":earns
                }
            }
        
        return routes

    def generate_all_job_combinations(self):
        job_combinations = {}
        for comb in itertools.permutations(self.routes_id,2):
            job0 = self.routes[comb[0]]['data']['dropoff']
            job1 = self.routes[comb[1]]['data']['pickup']

            job_combinations[f"{comb[0]}-{comb[1]}"] = {
                "from":comb[0],
                "to":comb[1],
                "combination":f"{comb[0]}-{comb[1]}",
                "distance":np.linalg.norm(job0-job1)
            }

        return job_combinations    

    
    def all_route_sequences(self):
        return list(itertools.permutations([k for k in self.routes]))


    def get_earnings(self,seq):
        earnings = 0
        distance = 0

        #from starting point 
        distance += np.linalg.norm(self.start_pos-self.routes[seq[0]]['data']['pickup'])
        if distance > self.bound:
            return earnings

        #jobs from the sequence 
        #and
        #from job to job, i.e. dropoff last-->pickup next    
        for j,job in enumerate(seq[:-1]):
            distance += self.routes[job]['data']['distance']
            if distance > self.bound:
                return earnings
            earnings += self.routes[job]['data']['earnings']

            distance += self.job_combinations[f'{job}-{seq[j+1]}']['distance']
            if distance > self.bound:
                return earnings

        #last job if possible
        distance += self.routes[seq[-1]]['data']['distance']
        if distance > self.bound:
            return earnings
        earnings += self.routes[seq[-1]]['data']['earnings']

        return earnings


    def brute_force(self,verbose=False):
        optimum_earnings = -1
        optimum_sequence = None
        all_sequences = self.all_route_sequences()
        N = len(all_sequences)

        for j,sequence in enumerate(all_sequences):
            earns =  self.get_earnings(sequence)
            if earns > optimum_earnings:
                optimum_earnings = earns
                optimum_sequence = sequence
            if j%100000 == 0 and verbose:
                print(f"Completion {(j/N*100):.2f}%")

        return optimum_earnings, optimum_sequence

    def get_naive_density(self):
        return np.array([self.routes[k]['data']['earnings']/self.routes[k]['data']['distance'] for k in self.routes])


    def get_true_sequence(self, seq):
        distance = 0

        distance += np.linalg.norm(self.start_pos-self.routes[seq[0]]['data']['pickup'])
        if distance > self.bound:
            return []
 
        for j,job in enumerate(seq[:-1]):
            distance += self.routes[job]['data']['distance']
            if distance > self.bound:
                return seq[:j]

            distance += self.job_combinations[f'{job}-{seq[j+1]}']['distance']
            if distance > self.bound:
                return seq[:j+1]

        distance += self.routes[seq[-1]]['data']['distance']
        if distance > self.bound:
            return seq[:-1]

        return seq

    def naive_strategy(self):
        naive_density = self.get_naive_density() 
        jobs = np.array([k for k in self.routes])
        sequence = jobs[np.argsort(naive_density)][::-1]

        return self.get_earnings(sequence), self.get_true_sequence(sequence) 


    def generate_potential_density_table(self):
        table = []
        for key,job in self.job_combinations.items():
            origin = job['from']
            dest = job['to']
            distance = job['distance'] + self.routes[origin]['data']['distance']
            earnings = self.routes[origin]['data']['earnings'] + self.routes[dest]['data']['earnings']
            density = earnings/distance

            table.append(
                [origin,
                dest,
                density]
            )
        
        return np.array(table)


    def potential_gains_strategy(self):
        potential_density = self.generate_potential_density_table()
        potential_density = potential_density[np.argsort(potential_density[:,2])][::-1]

        sequence = [] 
        sequence.append(potential_density[0,0])
        sequence.append(potential_density[0,1])
        
        sequence_set = set(sequence[0])
        sequence_set.add(sequence[1])

        for origin, dest, _ in potential_density[1:,:]:
            if origin == sequence[-1]:
                if dest not in sequence_set:
                    sequence_set.add(dest)
                    sequence.append(dest)


        return self.get_earnings(sequence),sequence


    def ant_colony_strategy(self, distance, start=None, ant_count=50, alpha=.5, beta=1.2,  pheromone_evaporation_coefficient=.40, pheromone_constant=1000.0, iterations=50):
        
        colony = ant_colony(self.routes, distance, start, ant_count, alpha, beta,  pheromone_evaporation_coefficient, pheromone_constant, iterations)
        sequence_ants = colony.mainloop()
        return self.get_earnings(sequence_ants), self.get_true_sequence(sequence_ants)



