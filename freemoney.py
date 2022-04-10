from turtle import update
import numpy as np
import matplotlib.pyplot as plt


class Offerer:
    def __init__(self,course_time, new_offer_p = 0.05, expire_p = 0.1, mean_offer = 100, std_offer = 10) -> None:
        self.current_time = 0
        self.course_time = course_time*60
        self.new_offer_p = new_offer_p
        self.expire_p = 0.1
        self.mean_offer = mean_offer
        self.std_offer = std_offer
        self.active_offers = []

    def on_time(self):        

        for t in range(self.course_time):
            self.current_time = t
        
            self.remove_offer()

            if np.random.random() < self.new_offer_p:
                offer = self.generate_offer()
                self.active_offers.append(offer) 

            yield self.course_time-self.current_time, self.active_offers    

    def remove_offer(self):
        for offer in self.active_offers:
            if np.random.random() < self.expire_p:
                self.active_offers.remove(offer)


    def generate_offer(self):
        return np.random.normal(self.mean_offer, self.std_offer)

    



class Strategy:
    def __init__(self, course_time):
        self.course_time = course_time
    
    def execute_strat(self, time_left, current_offer):
        pass

    def earns(self, current_offers):
        return np.max(current_offers)
    
    def reset(self):
        pass


class NaiveStrat(Strategy):
    def __init__(self, course_time, offer_tolerance, threshold = 120, panick_time=0.25):
        super().__init__(course_time)
        self.accumulated_offers = 0
        self.offers = np.array([])
        self.max_offer = 0
        self.offer_tolerance = offer_tolerance
        self.panick_time = panick_time
        self.threshold = threshold
        
    def __str__(self):
        return f"NaiveStrat risk={self.offer_tolerance}"

    def execute_strat(self, time_left, current_offers):
        _current_offers = np.array(current_offers)
        if _current_offers[_current_offers>120].shape[0] > 0:
            return True
        
        if self.offers == current_offers:
            self.accumulated_offers +=1
            self.offers = current_offers
            if np.max(self.offers) > self.max_offer:
                self.max_offer = np.max(self.offers)

        if (time_left < self.panick_time*self.course_time) and _current_offers.size:
            return True

        if self.accumulated_offers > self.offer_tolerance:
            if np.max(current_offers) > self.max_offer:
                return True

        return False

    def reset(self):
        self.accumulated_offers = 0
        self.offers = np.array([])
        self.max_offer = 0




class StatStrat(Strategy):
    def __init__(self, course_time, risk, update_frequency = 20):
        super().__init__(course_time)
        self.risk = risk
        self.A = None
        self.update_frequency = update_frequency

    def __str__(self):
        return f"StatStrat risk={self.risk}"

    def how_much_to_expect(self,time_remaining):
        self.A = self.A if self.A else []

        if time_remaining%self.update_frequency==0:
            A=[]
            for _ in range(5000):
                may_see_n_offers = np.random.binomial(time_remaining,0.05)
                if may_see_n_offers:
                    A+=[np.max(np.random.normal(100,10,may_see_n_offers))]
                else:
                    A+=[0]
            self.A = A
        
        return self.A


    def say_yes_treshold(self,time_remaining):
        return np.percentile(self.how_much_to_expect(time_remaining),self.risk)

    def execute_strat(self,time_remaining,current_offers):
        if current_offers:
            if max(current_offers) >= self.say_yes_treshold(time_remaining):
                return True
        return False




