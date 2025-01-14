import numpy as np
import random
import os
import glob
from itertools import permutations, combinations

# tools to generate and pseudo-randomize sequences of stimuli

def jitter_isi(value=0.2):
    '''Return a random jittered inter-stimulus interval'''
    return random.uniform(-value, value)

def get_cat_from_stim(stim: str):
    '''Extract the category from a stimulus path'''
    return os.path.basename(os.path.dirname(stim))

def draw_two(sequence, ignore_idx: list=None):
    ''' Returns two items and their positions in the sequence. Will ignore some indices if provided'''
    indices = random.sample(range(len(sequence)), 2)  # Get 2 unique indices
    if ignore_idx:
        while any([i in ignore_idx for i in indices]):
            indices = random.sample(range(len(sequence)), 2)
    return indices

def get_stims(input_dir, sequence, modality):
    '''Return the paths to the stimuli in the sequence'''
    stim_paths = []
    for item in sequence:
        stim = glob.glob(os.path.join(input_dir, 'stims', '*', f'{item}_{modality}.png'))[0]
        stim_paths.append(stim)
    return stim_paths

def count_dupes(arr):
    '''Count the number of duplicates in a list'''
    seen = set()
    duplicate_counter = 0
    for item in arr:
        if item in seen:
            duplicate_counter += 1
        else:
            seen.add(item)
    return duplicate_counter

def sample_n_throw(arr, n=3):
    '''Sample n items from a list and remove them'''
    sample = random.sample(set(arr), n)
    for s in sample:
        arr.remove(s)
    return sample, arr

def sample_until_no_dupes(arr, n=3):
    '''Sample n items from a list and remove them'''
    temp = arr.copy()
    sample, new_temp = sample_n_throw(temp, n)
    if count_dupes(new_temp) > 0:
        duplicate = True
        while duplicate:
            temp = arr.copy()
            sample, new_temp = sample_n_throw(temp, n)
            if count_dupes(new_temp) == 0:
                duplicate = False
    return sample, new_temp

def distribute_sequences_block(sequences: dict, n_blocks: int) -> dict:
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

def distribute_sequences_trial(sequence_names: list, n_trials: int) -> dict:
    ''' Distribute the sequences in the trials with no repetitions of the positions of elements'''
    orders = generate_orders_trial(sequence_names, n_trials)
    trials = {f"trial{i+1}": None for i in range(n_trials)}
    for i, _ in enumerate(trials):
        trials[f"trial{i+1}"] =orders[i]*2
    return trials

def generate_orders_trial(sequence_names: list, n_trials: int) -> list:
    ''' Return 3 sequences with unique positions of the elements'''

    orders = list(permutations(sequence_names, n_trials))
    pos_tracker = {key:0 for key in range(len(sequence_names))}
    unique_pos_seq = list()
    for order in orders:
        unique_pos = 0
        for i, seq in enumerate(order): # check if the position of the elements is unique
            if pos_tracker[i] == seq:
                continue
            else:
                unique_pos += 1
        if unique_pos == 3: # if all the elements had unique positions
            unique_pos_seq.append(order)
            for i, seq in enumerate(order):
                pos_tracker[i] = seq # update the position tracker

    return unique_pos_seq

def generate_sequences(input_dir, seq_structures, randomize=False):
    ''' Generate 6 unique amodal sequences. They are based on the fixed strucutres in seq_structures.
    The sequences are returned in a dict {name:order, ...}
    '''

    all_cat = sorted(os.listdir(os.path.join(input_dir, 'stims')))
    all_cat = [cat for cat in all_cat if not cat.startswith('.')] # remove .DS_store
    all_stims = {}
    for cat in all_cat:
        cat_stims = glob.glob(os.path.join(input_dir, 'stims', cat, '*img.png'))
        cat_stims = [os.path.basename(stim).split('_')[0] for stim in cat_stims]
        if randomize:
            random.shuffle(cat_stims)
        else:
            sorted(cat_stims)
        all_stims[cat] = cat_stims

    sequences = {}
    for i, (seq_name, seq_order) in enumerate(seq_structures.items()):
        seq = list()
        ordered_cat = [all_cat[j] for j in seq_order] # reorder the categries (strings format)
        for cat in ordered_cat:
            item = all_stims[cat][i] # extract the ith item in each category
            seq.append(item)
        sequences[seq_name] = seq
    
    return sequences

def generate_modalities(start_with_img=True):
    ''' Generate the order of modalities for a block'''
    if start_with_img:
        return ['img', 'txt']*3
    else:
        return list(np.random.permutation(['img', 'txt'])) * 3

def check_nstims(categories, input_dir):
    'Check if there is the same number of stim per class, raise error if not'
    counter = 0
    for i, cat in enumerate(categories.keys()):
        nstim = len(glob.glob(f"{input_dir}/stims/{cat}/*.png"))
        if i == 0:
            counter = nstim
        if nstim != counter:
            raise ValueError(f"Number of stim for category {cat} is different from the others")
        
def check_img_txt(input_dir):
    ''' Verifiy that for each text stim, there is a associated image stim.'''
    all_img = sorted(glob.glob(f"{input_dir}/stims/*/*img.png"))
    all_txt = sorted(glob.glob(f"{input_dir}/stims/*/*txt.png"))
    for img in all_img:
        txt = img.replace('img', 'txt')
        if txt not in all_txt:
            raise ValueError(f"Missing image for text stim {img}")
        
"""
********   TEST FUNCTIONS   *********
*                                     *
*  .----.                    .---.    *
* '---,  `.________________.'  _  `.  *
*      )   ________________   <_>  :  *
* .---'  .'                `.     .'  *
*  `----'                    `---'    *
*                                     *
***************************************
"""

# TODO: write a small file that tests all the important functions and run it before the experiment

def test_draw_two():

    seq = [0, 1, 2, 3, 4, 5]
    ignore_idx = [0, 1, 3, 4]
    indices = draw_two(seq, ignore_idx)
    assert indices not in [[0, 1], [1, 0], [3, 4], [4, 3]], "Indices should not be in ignore_idx"
    print("\o/ All tests passed for draw_two()")

def test_generate_sequences(input_dir, seq_structures):

    def check_no_dupe(randomize, n=100):
        ''' Check multiple times that there are no duplicates in the 6 generated sequences'''
        for i in range(n):
            seqs = generate_sequences(input_dir, seq_structures, randomize=randomize)
            keys = list(seqs.keys())
            all_items = [item for sublist in seqs.values() for item in sublist]
            assert len(keys) == 6, f"randomize={randomize}; Wrong number of sequences: {keys}"
            assert len(keys) == len(set(keys)), f"randomize={randomize}; Duplicate keys in {keys}, iteration {i}"
            assert len(all_items) == len(set(all_items)), f"randomize={randomize}; Duplicate items in {all_items}, iteration {i}"
    
    for randomize in [True, False]:
        check_no_dupe(randomize)

    def get_2_items_same_pos(randomize, n=10):
        ''' Fetch two items in the same position (same index of same sequence) in different iterations'''
        all_seqs = []
        for i in range(n):
            seqs = generate_sequences(input_dir, seq_structures, randomize=randomize)
            all_seqs.append(seqs)
        items1 = []
        items2 = []
        for i, seq1 in enumerate(all_seqs):
            if i == 0:
                continue
            seq2 = all_seqs[i-1]
            for j, key1 in enumerate(seq1.keys()):
                key2 = list(all_seqs[i-1].keys())[j]
                for k in range(len(seq1[key1])):
                    item1 = seq1[key1][k]
                    item2 = seq2[key2][k]
                    items1.append(item1)
                    items2.append(item2)
        return zip(items1, items2)
    
    n = 10
    n_pairs = (n-1) * 6 * 6
    pairs = get_2_items_same_pos(randomize=False, n=n)
    for item1, item2 in pairs:
        assert item1 == item2, "When param randomize=False, the sequences should be similar between iterations"
    
    pairs = get_2_items_same_pos(randomize=True, n=n)
    n_similar_items = sum([item1 == item2 for item1, item2 in pairs])
    assert n_similar_items != n_pairs, f"When param randomize=True, the sequences should be different between iterations"
    print(f'When randomize=True, the number of similar items: {n_similar_items} out of {n_pairs} pairs ({1/(n_pairs/n_similar_items)*100:.2f}%), should be around 16.66%')
    print("\o/ All tests passed for generate_sequences()")

### LEGACY FUNCTIONS

# not used in the current version of the experiment
def check_positions(blocks):
    ''' Check if the sequences are not in the same position in two blocks'''
    all_positions = {f"pos{i}": [] for i in range(len(blocks['block1']))}
    for block in blocks.values():
        for i, seq in enumerate(block):
            all_positions[f"pos{i}"].append(seq)
    for pos in all_positions.values():
        if count_dupes(pos) > 0:
            return False
    return True
    

def check_distribution(blocks):
    ''' Check if the distribution of 3 sequences blocks is not repeated.
    e.g. if ABC is in block1, it should not be in block2 whatever the order'''
     # NOT USED, its function is also passively covered by check_positions()
    all_sequences = []
    for block in blocks.values():
        com = list(permutations(block))
        com = [''.join(c) for c in com]
        all_sequences += com
    if count_dupes(all_sequences) > 0:
        return False
    return True

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

def generate_run_order(sequences, n_blocks=4):
    ''' Generate the run order, with the constraints that each sequence is presented in two different blocks,
     the sequences should not be in the same position in the two blocks, and all the transitions should be unique'''
    continue_sampling = True
    while continue_sampling:
        blocks = distribute_sequences_block(sequences, n_blocks=n_blocks)
        block_list = list(blocks.values())
        pairs = list(combinations(block_list, 2))
        n_pairs = len(pairs)
        passed_test = 0
        for pair in pairs:
            if check_transitions(pair[0], pair[1]):
                passed_test += 1
        if (passed_test == n_pairs) and (check_positions(blocks)):
                continue_sampling = False
    return blocks
