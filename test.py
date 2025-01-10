from src.stimuli_manager import distribute_sequences_trial
from src.params import input_dir, seq_structures
from itertools import combinations, permutations

seq_names = ['A', 'B', 'C']
trials = distribute_sequences_trial(seq_names, 3)
print(trials)