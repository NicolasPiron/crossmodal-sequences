import random
import pickle
# Generate random order, with minimal overlap between sequences:
# - the categories should have one position per sequence
# - the transitions should be unique between sequences

# Initial list of items
items = [0, 1, 2, 3, 4, 5]
labels = ['A', 'B', 'C', 'D', 'E', 'F']

def get_transitions(sequence):
    ''' Extract transitions from a sequence '''
    return [(sequence[i], sequence[i+1]) for i in range(len(sequence) - 1)]

def calculate_pairwise_differences(seq_structures):
    ''' Calculate pairwise positional differences between sequences '''
    keys = list(seq_structures.keys())
    n = len(keys)
    differences = {key: 0 for key in keys}
    for i in range(n):
        for j in range(i + 1, n):
            diff = 0
            for x, y in zip(seq_structures[keys[i]], seq_structures[keys[j]]): # zip the sequences together
                # to compare the elements by position
                if x != y:
                    diff += 1
            differences[keys[i]] += diff
            differences[keys[j]] += diff
    return differences

def generate_optimized_sequences(items, num_sequences, iterations=100000): # very high number of iterations to ensure a good solution
    ''' Generate sequences considering both unique transitions and maximizing positional differences'''
    best_score = 0
    best_sequences = None

    for _ in range(iterations):
        used_transitions = set()
        seq_structures = {}

        for i in range(num_sequences):
            attempts = 0
            while attempts < 1000:
                seq = list(items) # create a new sequence
                random.shuffle(seq) # shuffle the sequence
                transitions = get_transitions(seq)
                if all(t not in used_transitions for t in transitions): # check if the transitions are unique
                    seq_structures[i] = seq # add the sequence to the dictionary
                    used_transitions.update(transitions) # add the transitions to the set of used transitions
                    break
                attempts += 1
            else:
                # Restart if unable to create a valid sequence
                seq_structures.clear()
                used_transitions.clear()
                break

        if len(seq_structures) == num_sequences:
            differences = calculate_pairwise_differences(seq_structures)
            total_difference = sum(differences.values())
            if total_difference > best_score:
                best_score = total_difference
                best_sequences = seq_structures

    return best_sequences

# Generate optimized sequences
optimized_sequences = generate_optimized_sequences(items, 6)
# Convert the result to a list for display
optimized_sequences_list = [optimized_sequences[k] for k in sorted(optimized_sequences.keys())]
for i, seq in enumerate(optimized_sequences_list):
    print(seq)

# Save the optimized sequences to a file
with open('seq_structure.pkl', 'wb') as f:
    pickle.dump(optimized_sequences, f)
