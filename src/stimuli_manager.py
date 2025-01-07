import numpy as np
import random
import os
import glob

# tools to generate and pseudo-randomize sequences of stimuli

def get_cat_from_stim(stim):
    '''Extract the category from a stimulus path'''
    return os.path.basename(os.path.dirname(stim))

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

def generate_block_org(block_modalities=['img', 'txt'], sequences=[]):
    ''' Generate the order of modalities and sequence types for a block'''
    m_order = list(np.random.permutation(block_modalities)) * 3
    s_order = list(np.random.permutation(sequences)) * 2
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