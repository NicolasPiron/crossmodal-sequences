from utils.stimuli_manager import sample_n_throw, sample_until_no_dupes, generate_sequences, set_seed, count_dupes
from utils.params import input_dir, seq_structures
from itertools import combinations
from collections import Counter
from typing import List, Tuple

def distribute_sequences_block(sequences: dict, n_blocks: int) -> dict:
    ''' Distribute the sequences in the blocks with no repetitions inside each block.
    It also controls that the 6 sequences are all presented in the first two blocks'''

    def check_2_blocks(blocks: dict) -> bool:
        '''Check if the first two blocks contain all the sequences'''
        block1 = blocks['block1']
        block2 = blocks['block2']
        return True if count_dupes(block1+block2) == 0 else False

    all_unique_seq = list(sequences.keys())
    are_all_seq_presented = False

    while not are_all_seq_presented:
        all_seq_left = all_unique_seq*2
        blocks = {f"block{i+1}": [] for i in range(n_blocks)}
        for b in range(n_blocks):
            if b==2:
                seq_subset, all_seq_left = sample_until_no_dupes(all_seq_left) 
            else:
                seq_subset, all_seq_left = sample_n_throw(all_seq_left)
            blocks[f"block{b+1}"] = seq_subset
        are_all_seq_presented = check_2_blocks(blocks)

    return blocks


def generate_run_org() -> dict:

    def get_pairs(string:str) -> List[str]:
        '''Get the pairs of sequences in each block'''
        return [''.join(pair) for pair in combinations(string, 2)]
    
    def get_repeated_pairs(pairs:list) -> List[str]:
        ''' Return the repeated pairs in the list'''
        normalized_items = [''.join(sorted(item)) for item in pairs] # reorder the letters in each string
        counts = Counter(normalized_items)
        repeated_items = [item for item, count in counts.items() if count > 1]
        return repeated_items
    
    def get_unrepeated_seq(pairs:list, repeated_pairs) -> List[str]:
        ''' Return sequences that are not in repeated pairs'''
        pair_as_str = "".join(pairs)
        rep_pairs_as_str = "".join(repeated_pairs)
        unrepeated_seq = []
        for pair in pair_as_str:
            if (pair not in rep_pairs_as_str) and (pair not in unrepeated_seq):
                unrepeated_seq.append(pair)
        return unrepeated_seq

    def gen_one_run(sequences: dict) -> Tuple[dict, List[str]]:
        '''Generate one run with only 2 repeated pairs. Return the blocks, repeated pairs and unrepeated sequences'''
        two_rep_pairs = False
        while not two_rep_pairs: # Keep generating blocks until we get the best case scenario
            blocks = distribute_sequences_block(sequences, 4)
            pairs = []
            for block in blocks.values():
                pairs+=get_pairs(block)
            rep_pairs = get_repeated_pairs(pairs)
            unrep_seq = get_unrepeated_seq(pairs, rep_pairs)
            if len(rep_pairs)==2: # 2 repeated pairs (the best case scenario)
                two_rep_pairs = True
        return blocks, rep_pairs, unrep_seq
    
    sequences = generate_sequences(input_dir, seq_structures)
    # Generate two runs with unique repeated pairs between them (e.g. run1 AB, CF and run2 ED, FA)
    running = True
    while running:
        blocks1, rep_pairs1, unrep_seq1 = gen_one_run(sequences)
        blocks2, rep_pairs2, unrep_seq2 = gen_one_run(sequences)
        # condition 1 : the standalone sequences are different in the two runs
        four_standalone_seq = True if len(set(unrep_seq1+unrep_seq2))==4 else False
        # condition 2 : the repeated pairs are unique between the two runs
        counter = 0
        for pair in rep_pairs1:
            if pair not in rep_pairs2:
                counter+=1
        unique_repetitions = True if counter==2 else False
        if unique_repetitions and four_standalone_seq:
            running = False
            print(unrep_seq1, unrep_seq2)

    run_org = {'run1': blocks1, 'run2': blocks2}
    return run_org



print(generate_run_org())
    