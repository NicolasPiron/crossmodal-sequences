from src.stimuli_manager import draw_two, generate_sequences, get_cat_from_stim
from src.params import seq_structures, input_dir
import numpy as np

cat = get_cat_from_stim('/Users/pironn/Documents/PhD/experiment/crossmodal-sequences/data/output/animals/sub-00_run-01.csv')
print(cat)