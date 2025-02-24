import random
import pickle
from collections import Counter


def double_check(optimized_sequences):
    ''' Check that the optimized sequences are valid (unique triplets in all sequences)'''
    transitions = list()
    for seq in optimized_sequences.values():
        trans = get_transitions(seq, 3)
        for t in trans:
            transitions.append(t)
    if len(transitions) == len(set(transitions)):
        print('All triplets are unique')
    pairs = count_pairs_dist(optimized_sequences)
    if max(pairs.values()) < 4:
        print('No more than 3 repetitions of a pair')
    else:
        print('Too many repetitions of a pair')
    print('pair count:', pairs.values())
    return None

def count_pairs_dist(optimized_sequences):
    ''' Count the distribution of pairs in the optimized sequences '''
    pairs = list()
    for seq in optimized_sequences.values():
        pairs.extend(get_transitions(seq, 2))
    return Counter(pairs)

def get_transitions(sequence, n):
    ''' Extract transitions from a sequence ''' # redefined transitions as three elements
    if n==2:
        return [(sequence[i], sequence[i+1]) for i in range(len(sequence) - 1)]
    elif n==3:
        return [(sequence[i], sequence[i+1], sequence[i+2]) for i in range(len(sequence) - 2)]
    else:
        return None

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

def generate_optimized_sequences(items, num_sequences, iterations=200000): #  high number of iterations to ensure a good solution
    ''' Generate sequences considering both unique transitions and maximizing positional differences'''
    best_score = 0
    best_sequences = None

    for iter in range(iterations):
        if iter % 1000 == 0:
            print(f'Iteration {iter}')
        used_transitions = set()
        seq_structures = {}

        for i in range(num_sequences):
            attempts = 0
            while attempts < 1000:
                seq = list(items) # create a new sequence
                random.shuffle(seq) # shuffle the sequence
                transitions = get_transitions(seq, 3)
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
        
        pair_count = count_pairs_dist(seq_structures)
        n_rep = pair_count.values()
        if max(n_rep) < 4: # 3 seems to be the minimum number of repetitions of 12 sequences of 6 items
            if len(seq_structures) == num_sequences:
                differences = calculate_pairwise_differences(seq_structures)
                total_difference = sum(differences.values())
                if total_difference > best_score:
                    best_score = total_difference
                    best_sequences = seq_structures
                    
    return best_sequences, best_score

if __name__ == '__main__':

    items = [0, 1, 2, 3, 4, 5]
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'] # added 6 more labels

    scores = []
    sequences = []
    for i in range(100):
        optimized_sequences, best_score = generate_optimized_sequences(items, len(labels))
        scores.append(best_score)
        sequences.append(optimized_sequences)

    best_idx = scores.index(max(scores))
    optimized_sequences = sequences[best_idx]

    # Convert the result to a list for display
    optimized_sequences_list = [optimized_sequences[k] for k in sorted(optimized_sequences.keys())]
    for i, seq in enumerate(optimized_sequences_list):
        print(seq)

    # Save the optimized sequences to a file
    with open('seq_structure.pkl', 'wb') as f:
        pickle.dump(optimized_sequences, f)

    # Load the optimized sequences from a file
    # with open('seq_structure.pkl', 'rb') as f:
    #     optimized_sequences = pickle.load(f)

    # Double check the sequences
    double_check(optimized_sequences)