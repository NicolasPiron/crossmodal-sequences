from src.stimuli_manager import generate_sequences, sample_until_no_dupes, sample_n_throw, count_dupes
from src.params import input_dir, seq_structures
from itertools import combinations




# goal : create a function / set of functions that will allow to randomly organize how the sequences 
# are distributed in the blocks.
# Sequences = ['A', 'B', 'C', 'D', 'E', 'F', 'A', 'B', 'C', 'D', 'E', 'F']
# Blocks = 4

# we want three sequences in each block, and we want to make sure that :
# - each sequence is presented in two different blocks
# - the sequences should not be in the same position in the two blocks
# - all the transitions should be unique (e.g. no ABC, DEF, BCA, EFD, here BC and EF are repeated)
# Example of ideal output: {block1:[A,B,C], block2: [D,E,F], block3: [E,A,C], block4: [F,D,B]

# TODO:  ADD A CONSTRAINT : ABC SHOULD NOT BE IN TWO BLOCKS. No ABC, DEF, BCA, EFD.

import random

def distribute_sequences(sequences, n_blocks):
    ''' Distribute the sequences in the blocks with no repetitions'''
    all_sequences_left = list(sequences.keys())*2
    blocks = {f"block{i+1}": [] for i in range(n_blocks)}
    for b in range(n_blocks):
        if b==2:
            seq_subset, all_sequences_left = sample_until_no_dupes(all_sequences_left) 
        else:
            seq_subset, all_sequences_left = sample_n_throw(all_sequences_left)
        blocks[f"block{b+1}"] = seq_subset

    return blocks


def check_transitions(order1: str, order2: str):
    ''' Check if the transitions between two sequences are unique'''
    if order1 == order2:
        return False
    transitions = []
    for order in (order1, order2):
        order = ''.join(order)
        for i in range(len(order)-1):
            transitions.append(order[i:i+2])
    if count_dupes(transitions) > 0:
        return False
    
    return True

def generate_run_order():
    ''' Generate the run order'''
    sequences = generate_sequences(input_dir, seq_structures)

    continue_sampling = True
    while continue_sampling:
        
        blocks = distribute_sequences(sequences, 4)
        block_list = list(blocks.values())
        pairs = list(combinations(block_list, 2))
        n_pairs = len(pairs)
        passed_test = 0
        for pair in pairs:
            if check_transitions(pair[0], pair[1]):
                passed_test += 1
        if passed_test == n_pairs:
            continue_sampling = False

    return blocks


# # Example usage
sequences = ['A', 'B', 'C', 'D', 'E', 'F', 'A', 'B', 'C', 'D', 'E', 'F']
num_blocks = 4

# result = distribute_sequences(sequences, num_blocks)
# print(result)
# flag = check_transitions(['A', 'B', 'A'], ['C', 'B', 'A']) # should return True
# print(flag)
for i in range(10):
    blocks = generate_run_order()
    print(blocks)