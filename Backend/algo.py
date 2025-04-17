import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)  # Ensures reproducibility

def fitness_function(C, g, x, c):
    a = (1 - (g / C)) ** 2
    p = 1 - ((g / C) * x)
    d1i = (0.38 * C * a) / p

    a2 = 173 * (x ** 2)
    ri1 = np.sqrt((x - 1) + (x - 1) ** 2 + ((16 * x) / c))

    d2i = a2 * ri1

    return d1i + d2i

def fairness_penalty(green_times, congestion):
    penalty = 0
    for i in range(len(green_times)):
        for j in range(i + 1, len(green_times)):
            congestion_diff = abs(congestion[i] - congestion[j])
            if congestion_diff < 0.1:
                penalty += abs(green_times[i] - green_times[j])
    return penalty * 5

def initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars):
    population = []
    road_capacity = [20] * num_lights
    normalized_cars = np.array(cars) / np.max(cars)

    while len(population) < pop_size:
        green_times = np.random.randint(green_min, green_max + 1, num_lights)
        if np.sum(green_times) <= cycle_time:
            total_delay = np.sum([
                fitness_function(cycle_time, green_times[i], normalized_cars[i], road_capacity[i])
                for i in range(num_lights)
            ])
            fairness = fairness_penalty(green_times, normalized_cars)
            total_delay += fairness
            population.append((green_times, total_delay))
    return sorted(population, key=lambda x: x[1])

def roulette_wheel_selection(population, total_delays, beta):
    worst_delay = max(total_delays)
    probabilities = np.exp(-beta * np.array(total_delays) / worst_delay)
    probabilities /= np.sum(probabilities)
    return np.random.choice(len(population), p=probabilities)

def crossover(parent1, parent2, num_lights):
    point = np.random.randint(1, num_lights)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2

def mutate(individual, mutation_rate, green_min, green_max):
    num_lights = len(individual)
    mutated = individual.copy()
    for _ in range(int(mutation_rate * num_lights)):
        idx = np.random.randint(0, num_lights)
        sigma = np.random.choice([-1, 1]) * 0.02 * (green_max - green_min)
        mutated[idx] = np.clip(individual[idx] + sigma, green_min, green_max)
    return mutated

def inversion(individual, num_lights):
    idx1, idx2 = np.random.randint(0, num_lights, 2)
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
    individual[idx1:idx2+1] = individual[idx1:idx2+1][::-1]
    return individual

def genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars):
    population = initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars)
    best_sol = population[0]
    best_delays = [best_sol[1]]

    road_capacity = [20] * num_lights
    normalized_cars = np.array(cars) / np.max(cars)

    for _ in range(max_iter):
        total_delays = [ind[1] for ind in population]
        new_population = []

        while len(new_population) < pop_size:
            i1 = roulette_wheel_selection(population, total_delays, beta)
            i2 = roulette_wheel_selection(population, total_delays, beta)

            parent1, parent2 = population[i1][0], population[i2][0]
            child1, child2 = crossover(parent1, parent2, num_lights)

            for child in [child1, child2]:
                if np.sum(child) <= cycle_time:
                    child = mutate(child, mutation_rate, green_min, green_max)
                    child = np.clip(child, green_min, green_max)
                    total_delay = np.sum([
                        fitness_function(cycle_time, child[i], normalized_cars[i], road_capacity[i])
                        for i in range(num_lights)
                    ])
                    fairness = fairness_penalty(child, normalized_cars)
                    total_delay += fairness
                    new_population.append((child, total_delay))

        while len(new_population) < pop_size:
            i = np.random.randint(0, len(population))
            individual = inversion(population[i][0], num_lights)
            if np.sum(individual) <= cycle_time:
                individual = mutate(individual, mutation_rate, green_min, green_max)
                total_delay = np.sum([
                    fitness_function(cycle_time, individual[i], normalized_cars[i], road_capacity[i])
                    for i in range(num_lights)
                ])
                fairness = fairness_penalty(individual, normalized_cars)
                total_delay += fairness
                new_population.append((individual, total_delay))

        population += new_population
        population = sorted(population, key=lambda x: x[1])[:pop_size]

        if population[0][1] < best_sol[1]:
            best_sol = population[0]

        best_delays.append(best_sol[1])

    return best_sol, best_delays

def optimize_traffic(cars):
    pop_size = 400
    num_lights = 4
    max_iter = 25
    green_min = 10
    green_max = 60
    cycle_time = 160 - 12
    mutation_rate = 0.02
    pinv = 0.2
    beta = 8

    best_sol, best_delays = genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars)

    result = {
        'north': int(best_sol[0][0]),
        'south': int(best_sol[0][1]),
        'west': int(best_sol[0][2]),
        'east': int(best_sol[0][3])
    }

    print('Optimal Solution:')
    print(f'North Green Time = {result["north"]} seconds')
    print(f'South Green Time = {result["south"]} seconds')
    print(f'West Green Time = {result["west"]} seconds')
    print(f'East Green Time = {result["east"]} seconds')

    return result
