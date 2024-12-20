import numpy as np
import random
import os
import glob

# tools to generate and pseudo-randomize sequences of stimuli

def draw_two(sequence):
    ''' Returns two items and their positions in the sequence'''

    indices = random.sample(range(len(sequence)), 2)  # Get 2 unique indices
    return indices

def get_stims(input_dir, sequence, modality):
    '''Return the paths to the stimuli in the sequence'''

    stim_paths = []
    for item in sequence:
        stim = glob.glob(os.path.join(input_dir, 'stims', '*', f'{item}_{modality}.png'))[0]
        stim_paths.append(stim)

    return stim_paths

def reorg_seq(sequences, seq_structure):
    ''' Reorganize sequences according to the structure given in seq_structure'''

    assert len(sequences) == len(seq_structure), "Number of sequences and sequence structures must be the same"
    reorg_seq = {}
    for i, structure in enumerate(seq_structure.keys()):
    
        order = seq_structure[structure]
        seq = sequences[i]
        reorg_seq[structure] = ([seq[j] for j in order])
    
    return reorg_seq

def generate_sequences(n_amodal_items_per_cat, cat_mapping, input_dir):
    ''' Generate sequences of stimuli of length n_categories'''

    sequences = [list() for _ in range(n_amodal_items_per_cat)]

    for cat in cat_mapping.values():
        stims = glob.glob(f"{input_dir}/stims/{cat}/*.png")
        all_items = [os.path.basename(item).split('_')[0] for item in stims]
        unique_items = list(set(all_items))
        rand_order = np.random.permutation(unique_items)

        for i, seq in enumerate(sequences):
            seq.append(rand_order[i])

    return sequences

def generate_block_org(block_modalities=['img', 'txt'], block_seq_types=['A', 'B', 'C']):
    ''' Generate the order of modalities and sequence types for a block'''

    m_order = list(np.random.permutation(block_modalities)) * 3
    s_order = list(np.random.permutation(block_seq_types)) * 2

    return m_order, s_order


def check_nstims(cat_mapping, input_dir):
    'Check if there is the same number of stim per class, raise error if not'
    
    counter = 0
    for i, cat in enumerate(cat_mapping.values()):
        nstim = len(glob.glob(f"{input_dir}/stims/{cat}/*.png"))
        if i == 0:
            counter = nstim
        if nstim != counter:
            raise ValueError(f"Number of stim for category {cat} is different from the others")
        
