import sequences.stimuli_manager as sm 
from sequences.params import seq_structures, input_dir
import random

random.seed(42)

run_org = sm.generate_run_org(input_dir, seq_structures)
b=sm.generate_sequences(input_dir, seq_structures)
print(b)