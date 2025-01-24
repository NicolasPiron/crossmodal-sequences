from typing import Dict, List, Tuple
import random
import os
import glob
from pathlib import Path
from itertools import permutations, combinations
from collections import Counter
import sequences.params as pm

# tools to generate and pseudo-randomize sequences of stimuli

def w_and_set_seed(debugging:bool, out_dir:str)-> int:
    ''' Write a seed in a file and return it. If debugging is True, the seed is fixed to the one in params.py'''
    if debugging:
        seed = pm.seed
    else:
        seed = random.randint(0, 1000)
    random.seed(seed)
    w_seed(out_dir, seed)
    return seed

def w_seed(out_dir:str, seed:int)-> None:
    ''' Write the seed in a file'''
    seed_fn = Path(f"{out_dir}/seed.txt")
    with open(seed_fn, "w") as f:
        f.write(str(seed))

def r_and_set_seed(out_dir:str)-> None:
    ''' Read the seed from a file and set it'''
    seed_fn = Path(f"{out_dir}/seed.txt")
    with open(seed_fn, "r") as f:
        seed = f.read()
    random.seed(int(seed))
    return int(seed)

def jitter_isi(value:float=0.2)-> float:
    '''Return a random jittered inter-stimulus interval'''
    return random.uniform(-value, value)

def get_cat_from_stim(stim: str)-> str:
    '''Extract the category from a stimulus path'''
    return os.path.basename(os.path.dirname(stim))

def draw_two(ignore_idx: list=None):
    ''' Returns two items and their positions in the sequence. This function has been reworked to sample only 
    one item out of the 5 left. The 1st index will always be 0. '''
    idx2 = random.sample(range(1, 6), 1)
    if ignore_idx:
        # added this condition to avoid infinite loop. Because there are 5 items and 6 questions -> 1 item will be asked twice. 
        if len(ignore_idx) == 5:
            return (0, idx2[0])
        while any([i in ignore_idx for i in idx2]):
            idx2 = random.sample(range(1, 6), 1)
    return (0, idx2[0])

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

def generate_run_org(input_dir, seq_structures) -> dict:
    ''' Generate the organization of sequences in the runs. The function returns a dict with the blocks of each run.
    It controls that the sequences are well distributed between the two runs, with minimal overlap'''

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

    run_org = {'run1': blocks1, 'run2': blocks2}
    return run_org

def distribute_sequences_trial(sequence_names: List[str], n_trials: int) -> dict:
    ''' Distribute the sequences in the trials with no repetitions of the positions of elements'''
    orders = generate_orders_trial(sequence_names, n_trials)
    trials = {f"trial{i+1}": None for i in range(n_trials)}
    for i, _ in enumerate(trials):
        trials[f"trial{i+1}"] =orders[i]*2
    return trials

def distribute_mod_seq(n_block)-> Dict[str, List[str]]:
    ''' Distribute the modality of the first sequence of each trial between the blocks'''
    
    block_layouts = [(2, 1)] * 2 + [(1, 2)] * 2
    random.shuffle(block_layouts) # shuffle block layouts once
    block_org = {f'block{i + 1}': None for i in range(n_block)}
    for i, (img_count, txt_count) in enumerate(block_layouts):
        org = ['img']*img_count + ['txt']*txt_count
        random.shuffle(org) # shuffle the modalities
        block_org[f'block{i + 1}'] = org
    return block_org

def distribute_mod_quest(n_blocks: int, n_trials: int) -> Dict[str, Dict[str, Dict[str, int]]]:
    '''Fills a dictionary with the layout of trials question's modality.'''
    
    block_layouts = [(5, 4)] * 2 + [(4, 5)] * 2
    trial_layouts = {'more_img': [(2, 1)] * 2 + [(1, 2)],
                     'more_txt': [(2, 1)] + [(1, 2)] * 2}
   
    random.shuffle(block_layouts) # shuffle block layouts once
    block_org = { # unreadable dict comprehension to map the modalities by trial. déso
        f'block{i + 1}': {
            f'trial{j + 1}': {'img': None, 'txt': None}
            for j in range(n_trials)
        }
        for i in range(n_blocks)
    }
    # fill the block organization with the trial layouts
    for i, (img_count, txt_count) in enumerate(block_layouts):
        key = 'more_img' if img_count > txt_count else 'more_txt'
        t_layout = trial_layouts[key]
        random.shuffle(t_layout) # shuffle the three trial layouts' order
        for j, (n_img, n_txt) in enumerate(t_layout):
            block_org[f'block{i + 1}'][f'trial{j + 1}'] = ['img']*n_img + ['txt']*n_txt

    return block_org

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

def generate_sequences(input_dir, seq_structures):
    ''' Generate 6 unique amodal sequences. They are based on the fixed strucutres in seq_structures.
    The sequences are returned in a dict {name:order, ...}
    '''
    all_cat = sorted(os.listdir(os.path.join(input_dir, 'stims')))
    all_cat = [cat for cat in all_cat if not cat.startswith('.')] # remove .DS_store
    all_stims = {}
    for cat in all_cat:
        cat_stims = glob.glob(os.path.join(input_dir, 'stims', cat, '*img.png'))
        cat_stims = [os.path.basename(stim).split('_')[0] for stim in cat_stims]
        random.shuffle(cat_stims)
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
        return ['txt', 'img']*3

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

#############################################
 #             Question functions           #
#############################################

def get_slot_pos(y_pos):
    ''' Return the positions of the slots in the trial question'''
    return [(-0.45, y_pos), (-0.15, y_pos), (0.15, y_pos), (0.45, y_pos), (0.75, y_pos)]

def get_response_distance(correct_idx, response_idx, rt):
    ''' Return the distance between the correct and the response index. If the response time is 'NA', return 'NA' '''
    if rt == 'NA':
        return rt
    return abs(correct_idx - response_idx)

def get_feedback_args(distance):
    '''Return the feedback text and color based on the distance between the correct and the response index.
    The function also returns a boolean indicating if the response was correct'''
    feedback_map = {
        'NA': ("Trop lent!", "red", False, 0),
        0: ("Correct!\n+ 3pt", "green", True, 3),
    }
    return feedback_map.get(distance, ("Incorrect!\n+ 0pt", "red", False, 0))

def get_trial_feedback(n_points, max_points):
    '''Return the feedback text based on the number of points obtained'''
    if n_points == 0:
        return f"Dommage! Vous n'avez gagné aucun point sur {max_points}."
    elif n_points < max_points * 0.4:
        return f"Pas mal, vous avez gagné {n_points} points sur {max_points}. Continuez à essayer !"
    elif n_points < max_points * 0.7:
        return f"Bien joué! Vous avez obtenu {n_points} points sur {max_points}." 
    elif n_points < max_points:
        return f"Excellent! Vous avez presque réussi avec {n_points} points sur {max_points}."
    elif n_points == max_points:
        return f"Bravo! Score parfait : {n_points} sur {max_points} !"
    
def get_reward_sound(reward_sounds, n_points):
    ''' Return the reward sound based on the number of points obtained for this question.'''
    if n_points < 3:
        return None
    elif n_points == 3:
        return reward_sounds[2]
    else:
        raise ValueError(f"Invalid number of points: {n_points}")

def run_question(tools, slots, start_item, end_item, rt_clock, global_clock, t_act):
    '''Run a question where the participant has to place the second item in the correct position.
    NB : it adds 1 to the returned index to takes into account the first item of the sequence (which is not
    selectable)'''

    wait_fun = tools['wait_fun']
    event_fun = tools['event_fun']
    clear_event_fun = tools['clear_event_fun']
    trig_fun = tools['trig_fun']

    def draw_all():
        ''' Draw the slots, the start item and the background'''
        tools['background'].draw()
        for slot in slots:
            slot["rect"].draw()
            slot["highlight"].draw()
        start_item.draw()
        start_item.draw()
        end_item.draw()

    def reset_highlight(slots):
        ''' Reset the highlight of all slots before the next question'''
        for slot in slots:
            slot["highlight"].opacity = 0

    # if tools['debugging']:
    #     t_act = 2
    iterations = 0
    current_index = 0
    highlight_onset = None
    running = True
    global_clock.reset()

    while running:

        draw_all()
        tools['win'].flip()

        if iterations == 0:
            wait_fun(0.01)
            clear_event_fun()
        else:
            if highlight_onset is None:
                slots[current_index]["highlight"].opacity = 1
                highlight_onset = True

            keys = event_fun()

            if "left" in keys:
                current_index = move_highlight(slots, current_index=current_index, direction="left")
                tools['logger'].info(f"Left key pressed, current index: {current_index+1}")

            if "right" in keys:
                current_index = move_highlight(slots, current_index=current_index, direction="right")
                tools['logger'].info(f"Right key pressed, current index: {current_index+1}")

            if "space" in keys:
                trig_fun(current_index+101) # trigger is the slot index + 101 TODO: change this to something adaptive
                resp_time = rt_clock.getTime()
                global_clock.reset() # reset the global clock to avoid time out
                reset_highlight(slots)
                end_item.pos = slots[current_index]["rect"].pos # move the end item to the selected slot
                draw_all()
                tools['win'].flip()
                tools['logger'].info('Space key pressed')
                tools['logger'].info(f'Index selected: {current_index+1}')
                tools['logger'].info(f'RT: {resp_time}')
                wait_fun(1)
                running = False

            if "escape" in keys:
                running = False

            if global_clock.getTime() > t_act:
                trig_fun(200) 
                tools['logger'].info('Time out')
                tools['logger'].info(f'clock time: {global_clock.getTime()}')
                running = False
                resp_time = 'NA'
                reset_highlight(slots)
        
        iterations += 1

    return current_index+1, resp_time

def move_highlight(slots, current_index, direction=None):
    ''' Move the highlight to the next or previous slot depending on direction
    
    Parameters
    ----------
    slots : list
        List of slot objects
    current_index : int
        The current index of the highlighted slot
    direction : str
        The direction of the movement, either "left" or "right"

    Returns
    -------
    int
        The new index of the highlighted slot
    '''
    # Reset all highlights
    for slot in slots:
        slot["highlight"].opacity = 0
    if direction == "left":
        if current_index > 0:
            current_index -= 1
        else:
            current_index = len(slots) - 1
    elif direction == "right":
        if current_index < len(slots) - 1:
            current_index += 1
        else:
            current_index = 0
    # Set the highlight on the current slot
    slots[current_index]["highlight"].opacity = 1
    return current_index
        
def fade_out(tools, obj, clock, f_dur):
    ''' Fade out the object'''
    clock.reset()
    while clock.getTime() < f_dur:
        elapsed_time = clock.getTime()
        opacity = 1.0 - (elapsed_time / f_dur)  # linear fade-out
        obj.opacity = max(0.0, opacity)  # ensure opacity doesn't go below 0
        tools['background'].draw()
        obj.draw()
        tools['win'].flip()

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

def test_distribute_mod_quest():
    # test because it's tidious to check visually
    block_org = distribute_mod_quest(4, 3)
    total_img = 0
    total_txt = 0
    for block in block_org.values():
        for trial in block.values():
            total_img += trial.count('img')
            total_txt += trial.count('txt')
    assert total_img == total_txt
    assert total_img == 18
    assert total_txt == 18
    print('All tests passed for test_distribute_mod_quest()!')

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
    assert n_similar_items != n_pairs, "When param randomize=True, the sequences should be different between iterations"
    print(f'When randomize=True, the number of similar items: {n_similar_items} out of {n_pairs} pairs ({1/(n_pairs/n_similar_items)*100:.2f}%), should be around 16.66%')
    print("\o/ All tests passed for generate_sequences()")
 
 
'''
*** LEGACY FUNCTIONS ****
*      \_______/        *
*  `.,-'\_____/`-.,'    *
*   /`..'\ _ /`.,'\     *
*  /  /`.,' `.,'\  \    *
* /__/__/     \__\__\__ *
* \  \  \     /  /  /   * 
*  \  \,'`._,'`./  /    *
*   \,'`./___\,'`./     *
*  ,'`-./_____\,-'`.    *
*      /       \        *
*************************   
'''

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
