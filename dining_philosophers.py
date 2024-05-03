import heapq
import random
import matplotlib.pyplot as plt
from enum import IntEnum
from argparse import ArgumentParser


class EventTypes(IntEnum):
    
    REQUEST = 0
    FINISH = 1

 
class Chopstick:
    
    def __init__(self):
        self.is_free = True

    def pick_up(self):
        self.is_free = False
    
    def put_down(self):
        self.is_free = True
 

class Philosopher:
    
    def __init__(self, mi, lambda_i):
        self.mi = mi
        self.lambda_i = lambda_i
        self.left_chopstick = None
        self.right_chopstick = None
        self.failed_attempts = 0
        self.eating_time = 0
        self.started_at = 0
        self.requests = []

    def request(self, time):
        self.requests.append(time)
        if self.left_chopstick.is_free and self.right_chopstick.is_free:
            self.left_chopstick.pick_up()
            self.right_chopstick.pick_up()
            self.started_at = time
            return Event(self, time + random.expovariate(self.mi), EventTypes.FINISH)
        else:
            self.failed_attempts += 1
            return Event(self, time + random.expovariate(self.lambda_i), EventTypes.REQUEST)
    
    def finish(self, time):
        self.left_chopstick.put_down()
        self.right_chopstick.put_down()
        self.eating_time += (time - self.started_at)
        return Event(self, time + random.expovariate(self.lambda_i), EventTypes.REQUEST)


class Event:
    
    def __init__(self, philosopher, time, event_type):
        self.philosopher = philosopher
        self.time = time
        self.type = event_type

    def __lt__(self, other):
        return self.time < other.time


class Simulation:
    
    def __init__(self, mi, T, lambdas):
        self.events = []
        self.T = T
        self.philosophers = [Philosopher(mi, lambda_i) for lambda_i in lambdas]
        chopsticks = [Chopstick() for _ in self.philosophers]
        for index, philospher in enumerate(self.philosophers):
            philospher.left_chopstick = chopsticks[index]
            philospher.right_chopstick = chopsticks[(index + 1) % len(chopsticks)]
        
    def run(self):
        time = 0
        for philosopher in self.philosophers:
            heapq.heappush(self.events, philosopher.request(time))
        while time < self.T:
            event = heapq.heappop(self.events)
            time = event.time
            if event.type == EventTypes.REQUEST:
                next_event = event.philosopher.request(time)
            elif event.type == EventTypes.FINISH:
                next_event = event.philosopher.finish(time)
            heapq.heappush(self.events, next_event)
        self.events.clear()
    
    def plot(self):
        eating_times = [philosopher.eating_time for philosopher in self.philosophers]
        plt.subplot(221)
        plt.bar(range(1, len(self.philosophers) + 1), eating_times)
        plt.xticks(range(1, len(self.philosophers) + 1))
        plt.xlabel("Philosopher")
        plt.ylabel("Eating time")
        failed_attempts = [philosopher.failed_attempts for philosopher in self.philosophers]
        plt.subplot(222)
        plt.bar(range(1, len(self.philosophers) + 1), failed_attempts)
        plt.xticks(range(1, len(self.philosophers) + 1))
        plt.xlabel("Philosopher")
        plt.ylabel("Failed attempts")
        plt.subplot(212)
        for philosopher in self.philosophers:
            plt.scatter(philosopher.requests, range(len(philosopher.requests)))
        plt.xlabel("Time")
        plt.ylabel("Philosopher's requests")
        plt.text(0.1, 0.9, 
                 f"mi: {self.philosophers[0].mi}\n"
                 f"lambdas: {[philosopher.lambda_i for philosopher in self.philosophers]}\n"
                 f"T: {self.T}\n",
                 fontsize=14, transform=plt.gcf().transFigure)
        mng = plt.get_current_fig_manager()
        mng.set_window_title('Dining philosophers')
        mng.window.state('zoomed')
        plt.show()


def run(n, T, mi = None, lambdas = None):
    if mi is None:
        mi = round(random.uniform(0.01, 1), 2)
    if lambdas is None:
        lambdas = [round(random.uniform(0.01, 1), 2) for _ in range(n)]
    simulation = Simulation(mi, T, lambdas)
    simulation.run()
    return simulation
 

if __name__ == "__main__":
    parser = ArgumentParser(description='Dining philosophers')
    parser.add_argument('-n', type=int, default=5, help='Number of philosophers')
    parser.add_argument('-T', type=int, default=500, help='Time of simulation')
    parser.add_argument('-mi', type=float, help='mi')
    parser.add_argument('-lambdas', type=float, nargs='*', help='lambdas')
    args = parser.parse_args()
    if args.lambdas:
        args.n = len(args.lambdas)
    if args.n < 2 or args.n % 2 != 1:
        raise ValueError("Number of philosophers must be odd and greater than 1")
    if args.T < 1:
        raise ValueError("Time of simulation must be greater than 0")
    if args.mi and args.mi <= 0:
        raise ValueError("Mi must be greater than 0")
    if args.lambdas and any(lambda_i <= 0 for lambda_i in args.lambdas):
        raise ValueError("Lambdas must be greater than 0")

    if args.mi and args.lambdas:
        print(f"mi = {args.mi}")
        print(
            f"lambdas = {[lambda_i for lambda_i in args.lambdas]}"
        )
        run(args.n, args.T, args.mi, args.lambdas).plot()
    else:
        while True:
            simulation = run(args.n, args.T, args.mi, args.lambdas)
            if any(philosopher.eating_time < args.T * 0.01 for philosopher in simulation.philosophers):
                philosopher = next(
                    philosopher
                    for philosopher in simulation.philosophers
                    if philosopher.eating_time < args.T * 0.01
                )
                simulation.plot()
                break
