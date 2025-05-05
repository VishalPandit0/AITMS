import numpy as np

def fitness_function(C, g, x, c, has_ambulance=False):
    if has_ambulance:
        return 0.01 * C * (1 - (g / C))  # Minimal but variable delay
    
    a = (1 - (g / C)) ** 2
    p = 1 - ((g / C) * x)
    d1i = (0.38 * C * a) / (p + 1e-6)
    
    a2 = 173 * (x ** 2)
    ri1 = np.sqrt(np.maximum((x - 1) + (x - 1) ** 2 + ((16 * x) / c), 0))
    d2i = a2 * ri1

    return (d1i + d2i) * (x + 0.5)

def fairness_penalty(green_times, congestion, ambulance_flags):
    penalty = 0
    for i in range(len(green_times)):
        for j in range(i + 1, len(green_times)):
            if ambulance_flags[i] or ambulance_flags[j]:
                continue
            congestion_diff = abs(congestion[i] - congestion[j])
            if congestion_diff < 0.2:
                weight = 1 - (congestion_diff / 0.2)
                penalty += weight * abs(green_times[i] - green_times[j])
    return penalty * 2

def initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, traffic_data):
    population = []
    road_capacity = [20] * num_lights
    vehicle_counts = np.array([td['vehicle_count'] for td in traffic_data])
    ambulance_flags = [td['ambulance_detected'] for td in traffic_data]
    ambulance_count = sum(ambulance_flags)
    remaining_time = cycle_time - ambulance_count * green_max

    while len(population) < pop_size:
        non_ambulance_counts = vehicle_counts * (1 - np.array(ambulance_flags))
        if np.sum(non_ambulance_counts) > 0:
            base_times = green_min + (non_ambulance_counts / np.sum(non_ambulance_counts)) * (remaining_time - (num_lights - ambulance_count) * green_min)
        else:
            base_times = np.full(num_lights, green_min)
        
        base_times = np.round(base_times).astype(int)
        green_times = np.clip(base_times + np.random.randint(-5, 6, num_lights), green_min, green_max)
        
        for i in range(num_lights):
            if ambulance_flags[i]:
                green_times[i] = green_max
                
        if np.sum(green_times) <= cycle_time:
            total_delay = np.sum([ 
                fitness_function(cycle_time, green_times[i], 
                                vehicle_counts[i] / max(1, max(vehicle_counts)), 
                                road_capacity[i], ambulance_flags[i]) 
                for i in range(num_lights)
            ])
            fairness = fairness_penalty(green_times, 
                                       vehicle_counts / max(1, max(vehicle_counts)), 
                                       ambulance_flags)
            total_delay += fairness
            population.append((green_times, total_delay))

    return sorted(population, key=lambda x: x[1])

def roulette_wheel_selection(population, total_delays, beta):
    worst_delay = max(total_delays)
    total_delays = np.nan_to_num(total_delays, nan=worst_delay * 2)
    probabilities = np.exp(-beta * np.array(total_delays) / worst_delay)
    probabilities /= np.sum(probabilities)
    return np.random.choice(len(population), p=probabilities)

def crossover(parent1, parent2, num_lights):
    point = np.random.randint(1, num_lights)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2

def mutate(individual, mutation_rate, green_min, green_max, normalized_cars, ambulance_flags):
    mutated = individual.copy()
    for i in range(len(individual)):
        if ambulance_flags[i]:
            continue  # Don't mutate ambulance lanes
        if np.random.random() < mutation_rate:
            mutation_size = max(1, int(0.1 * (green_max - green_min) * (i + 1) / len(individual)))
            if normalized_cars[i] < 0.1:
                mutation_size = min(mutation_size, 2)
            mutated[i] = np.clip(individual[i] + np.random.randint(-mutation_size, mutation_size + 1),
                                green_min, green_max)
    return mutated

def genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, 
                     cycle_time, mutation_rate, pinv, beta, traffic_data):
    population = initialize_population(pop_size, num_lights, green_min, green_max, 
                                     cycle_time, traffic_data)
    best_sol = population[0]

    road_capacity = [20] * num_lights
    vehicle_counts = np.array([td['vehicle_count'] for td in traffic_data])
    max_vehicles = max(1, max(vehicle_counts))
    normalized_cars = vehicle_counts / max_vehicles
    ambulance_flags = [td['ambulance_detected'] for td in traffic_data]

    for iteration in range(max_iter):
        total_delays = [ind[1] for ind in population]
        new_population = []

        while len(new_population) < pop_size:
            i1 = roulette_wheel_selection(population, total_delays, beta)
            i2 = roulette_wheel_selection(population, total_delays, beta)

            parent1, parent2 = population[i1][0], population[i2][0]
            child1, child2 = crossover(parent1, parent2, num_lights)

            for child in [child1, child2]:
                # Ensure ambulance lanes get max time
                for i in range(num_lights):
                    if ambulance_flags[i]:
                        child[i] = green_max
                
                # Redistribute remaining time
                remaining_time = cycle_time - sum(child[i] for i in range(num_lights) if ambulance_flags[i])
                non_ambulance_indices = [i for i in range(num_lights) if not ambulance_flags[i]]
                
                if len(non_ambulance_indices) > 0:
                    total_non_ambulance = sum(child[i] for i in non_ambulance_indices)
                    if total_non_ambulance > remaining_time:
                        scale = remaining_time / total_non_ambulance
                        for i in non_ambulance_indices:
                            child[i] = max(green_min, min(green_max, int(child[i] * scale)))
                
                if np.sum(child) <= cycle_time:
                    child = mutate(child, mutation_rate, green_min, green_max, 
                                   normalized_cars, ambulance_flags)
                    total_delay = np.sum([
                        fitness_function(cycle_time, child[i], normalized_cars[i], 
                                        road_capacity[i], ambulance_flags[i])
                        for i in range(num_lights)
                    ])
                    fairness = fairness_penalty(child, normalized_cars, ambulance_flags)
                    total_delay += fairness
                    new_population.append((child, total_delay))

        population += new_population
        population = sorted(population, key=lambda x: x[1])[:pop_size]

        if population[0][1] < best_sol[1]:
            best_sol = population[0]

    return best_sol

def optimize_traffic(traffic_data):
    pop_size = 150
    num_lights = 4
    max_iter = 30
    green_min = 10
    green_max = 60
    cycle_time = 148  # 160 - 12 (buffer)
    mutation_rate = 0.05
    pinv = 0.3
    beta = 6

    best_sol = genetic_algorithm(
        pop_size, num_lights, max_iter, green_min, green_max,
        cycle_time, mutation_rate, pinv, beta, traffic_data
    )

    directions = ['lane1', 'lane2', 'lane3', 'lane4']
    lane_data = []

    for i, direction in enumerate(directions):
        lane_data.append({
            'direction': direction,
            'vehicle_count': traffic_data[i]['vehicle_count'],
            'ambulance_detected': traffic_data[i]['ambulance_detected'],
            'green_time': int(best_sol[0][i])
        })

    ambulance_lanes = [lane for lane in lane_data if lane['ambulance_detected']]
    non_ambulance_lanes = [lane for lane in lane_data if not lane['ambulance_detected']]

    for lane in ambulance_lanes:
        lane['priority'] = 1

    sorted_non_ambulance = sorted(non_ambulance_lanes, key=lambda x: -x['vehicle_count'])
    for i, lane in enumerate(sorted_non_ambulance):
        lane['priority'] = i + 2

    final_data = ambulance_lanes + sorted_non_ambulance

    return {
        "lane1": next(l['green_time'] for l in final_data if l['direction'] == 'lane1'),
        "lane2": next(l['green_time'] for l in final_data if l['direction'] == 'lane2'),
        "lane3": next(l['green_time'] for l in final_data if l['direction'] == 'lane3'),
        "lane4": next(l['green_time'] for l in final_data if l['direction'] == 'lane4'),
        "priority": {l['direction']: l['priority'] for l in final_data},
        "ambulance_detected": {l['direction']: l['ambulance_detected'] for l in final_data}
    }