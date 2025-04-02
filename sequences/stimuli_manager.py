from typing import Dict, List, Tuple
import random
import os
import glob
from itertools import permutations, combinations
from collections import Counter, defaultdict

# tools to generate and pseudo-randomize sequences of stimuli

def distribute_tones(tone_names:List[str], seq_names:List[str])-> Dict[str, str]:
    ''' Attribute a tone to each sequence. This is done randomly for each participant.'''
    random.shuffle(tone_names)
    tone_dict = {}
    for i, seq in enumerate(seq_names):
        tone_dict[seq] = tone_names[i]
    return tone_dict

def get_tone_name(input_dir:str)-> List[str]:
    ''' '''
    ...

def set_seed(subject_id:str)-> int:
    ''' Write a seed in a file and return it. The seed is based on the subject ID'''
    seed = int(subject_id)
    random.seed(seed)
    return seed

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

def get_stims(input_dir:str, sequence:List[str], modality:str, lang:str)-> List[str]:
    '''Return the paths to the stimuli in the sequence'''
    stim_paths = []
    for item in sequence:
        stim = glob.glob(os.path.join(input_dir, 'stims', lang, '*', f'{item}_{modality}.png'))[0]
        stim_paths.append(stim)
    return stim_paths

def count_dupes(arr:List)-> int:
    '''Count the number of duplicates in a list'''
    seen = set()
    duplicate_counter = 0
    for item in arr:
        if item in seen:
            duplicate_counter += 1
        else:
            seen.add(item)
    return duplicate_counter

def sample_n_throw(arr:List, n:int=3) -> Tuple[List, List]:
    '''Sample n items from a list and remove them'''
    sample = random.sample(sorted(set(arr)), n)
    for s in sample:
        arr.remove(s)
    return sample, arr

def sample_until_no_dupes(arr:List, n:int=3) -> Tuple[List, List]:
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

def distribute_sequences_run(seq_names: list, n_runs: int) -> Dict[str, List[str]]:
    ''' Distribute the sequences in the runs with no repetitions inside each run.
    Returns a dict that looks like that : {'run1': ['I', 'A', 'F', 'E', 'G', 'J'], 'run2': ['L', 'C', 'H', 'B', 'D', 'K']}
    '''
    random.shuffle(seq_names)
    result = defaultdict(list)
    for i, seq in enumerate(seq_names): # go name by name to fill the runs
        run_key = f"run{i % n_runs + 1}"  # this cycles through the runs
        result[run_key].append(seq)
    return dict(result)

def distribute_sequences_block(seq_names: list, n_blocks: int) -> Dict[str, List[str]]:
    ''' Distribute the sequences in the blocks with no repetitions inside each block.
    It also controls that the 6 sequences are all presented in the first two blocks.
    Returns dict that looks like this: {'block1': ['L', 'E', 'G'], 'block2':[...], ...}
    '''

    def check_2_blocks(blocks: dict) -> bool:
        '''Check if the first two blocks contain all the sequences'''
        block1 = blocks['block1']
        block2 = blocks['block2']
        return True if count_dupes(block1+block2) == 0 else False

    are_all_seq_presented = False

    while not are_all_seq_presented:
        all_seq_left = seq_names*2
        blocks = {f"block{i+1}": [] for i in range(n_blocks)}
        for b in range(n_blocks):
            if b==2:
                seq_subset, all_seq_left = sample_until_no_dupes(all_seq_left) 
            else:
                seq_subset, all_seq_left = sample_n_throw(all_seq_left)
            blocks[f"block{b+1}"] = seq_subset
        are_all_seq_presented = check_2_blocks(blocks)

    return blocks

def generate_run_org(sequences:Dict[str, List], seed) -> Dict[str, Dict[str, List[str]]]:
    ''' Generate the organization of sequences in the runs. The function returns a dict with the blocks of each run.
    It controls that the sequences are well distributed between the two runs.
    If the experiment crashes, the splits will stay the same, but the blocks org will change. This is due to the
    non replicable randomization in distribute_sequences_block(). At least if a seed is set, the two runs will be made
    of different sequences.

    sequences = {'A': ['item1', 'item2', ...], 'B': [...], ...}
    
    Returns dict that looks like this: {'run1': {'block1': ['L', 'E', 'G'], 'block2':[...], ...}, 'run2': {...}}
    '''

    def get_pairs(string:str) -> List[str]:
        '''Get the pairs of sequences in each block'''
        return [''.join(pair) for pair in combinations(string, 2)]
    
    def get_repeated_pairs(pairs:list) -> List[str]:
        ''' Return the repeated pairs in the list'''
        normalized_items = [''.join(sorted(item)) for item in pairs] # reorder the letters in each string
        counts = Counter(normalized_items)
        repeated_items = [item for item, count in counts.items() if count > 1]
        return repeated_items

    def gen_one_run(sequences: List) ->  Dict[str, List[str]]:
        '''Generate one run with only 2 repeated pairs.
        Returned dict looks like this {'block1': ['L', 'E', 'G'], 'block2':[...], ...}'''
        two_rep_pairs = False
        while not two_rep_pairs: # Keep generating blocks until we get the best case scenario
            blocks = distribute_sequences_block(sequences, 4)
            pairs = []
            for block in blocks.values():
                pairs+=get_pairs(block)
            rep_pairs = get_repeated_pairs(pairs)
            if len(rep_pairs)==2: # 2 repeated pairs (the best case scenario)
                two_rep_pairs = True
        return blocks
    
    random.seed(seed) # has to set again because the function is called multiple times
    seq_names = list(sequences.keys())
    seq_separated = distribute_sequences_run(seq_names, 2)
    run_org = {
        'run1': gen_one_run(seq_separated['run1']),
        'run2': gen_one_run(seq_separated['run2'])
    }
    return run_org

def distribute_sequences_trial(sequence_names: List[str], n_trials: int) -> Dict[str, List[str]]:
    ''' Distribute the sequences in the trials with no repetitions of the positions of elements
    Returns a dict that looks like this: {'trial1': ['A', 'B', 'C', 'A', 'B', 'C'], 'trial2': [...], ...}
    '''
    orders = generate_orders_trial(sequence_names, n_trials)
    trials = {f"trial{i+1}": None for i in range(n_trials)}
    for i, _ in enumerate(trials):
        trials[f"trial{i+1}"] =orders[i]*2
    return trials

def distribute_mod_seq(n_block:int)-> Dict[str, List[str]]:
    ''' Distribute the modality of the first sequence of each trial between the blocks
    Returns a dict that looks like this: {'block1': ['img', 'txt', 'img'], 'block2': [...], ...}
    '''
    
    block_layouts = [(2, 1)] * 2 + [(1, 2)] * 2
    random.shuffle(block_layouts) # shuffle block layouts once
    block_org = {f'block{i + 1}': None for i in range(n_block)}
    for i, (img_count, txt_count) in enumerate(block_layouts):
        org = ['img']*img_count + ['txt']*txt_count
        random.shuffle(org) # shuffle the modalities
        block_org[f'block{i + 1}'] = org
    return block_org

def distribute_mod_quest(n_blocks: int, n_trials: int) -> Dict[str, Dict[str, List[str]]]:
    ''' Fills a dictionary with the layout of trials question's modality.
    Returned dict looks like this: {'block1': {'trial1': ['img', 'txt', 'txt'], 'trial2': ['img',...], ...}, 'block2': {...}, ...}
    '''
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

def generate_orders_trial(sequence_names: list, n_trials: int) -> List[Tuple[str]]:
    ''' Return 3 orders of sequence names: The position of each unique elements is unique.
    Returns this kind of list [('A', 'B', 'C'), ('B', 'C', 'A'), ('C', 'A', 'B')]
    '''
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

def generate_sequences(input_dir:str, seq_structures:Dict, lang:str)-> Dict[str, List[str]]:
    ''' Generate 6 unique amodal sequences. They are based on the fixed strucutres in seq_structures.
    The sequences are returned in a dict {'A':[item1, 'item2', ...], ...}
    '''
    all_cat = sorted(os.listdir(os.path.join(input_dir, 'stims', lang)))
    all_cat = [cat for cat in all_cat if not cat.startswith('.')] # remove .DS_store
    all_stims = {}
    for cat in all_cat:
        cat_stims = glob.glob(os.path.join(input_dir, 'stims', lang, cat, '*img.png'))
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

def check_nstims(categories, input_dir, lang):
    'Check if there is the same number of stim per class, raise error if not'
    counter = 0
    for i, cat in enumerate(categories.keys()):
        nstim = len(glob.glob(f"{input_dir}/stims/{lang}/{cat}/*.png"))
        if i == 0:
            counter = nstim
        if nstim != counter:
            raise ValueError(f"Number of stim for category {cat} is different from the others")
        
def check_img_txt(input_dir, lang):
    ''' Verifiy that for each text stim, there is a associated image stim.'''
    all_img = sorted(glob.glob(f"{input_dir}/stims/{lang}/*/*img.png"))
    all_txt = sorted(glob.glob(f"{input_dir}/stims/{lang}/*/*txt.png"))
    for img in all_img:
        txt = img.replace('img', 'txt')
        if txt not in all_txt:
            raise ValueError(f"Missing image for text stim {img}")

#############################################
 #             Question functions           #
#############################################

def get_slot_pos(y_pos:float)-> List[Tuple[float]]:
    ''' Return the positions of the slots in the trial question'''
    return [(-0.45, y_pos), (-0.15, y_pos), (0.15, y_pos), (0.45, y_pos), (0.75, y_pos)]

def get_response_distance(correct_idx:int, response_idx:int, rt:float)-> int:
    ''' Return the distance between the correct and the response index. If the response time is 'NA', return 'NA' '''
    if rt == 'NA':
        return rt
    return abs(correct_idx - response_idx)

def get_feedback_args(distance:int, lang:str)-> Tuple[str, str, bool, int]:
    '''Return the feedback text and color based on the distance between the correct and the response index.
    The function also returns a boolean indicating if the response was correct'''
    if lang == 'fr':
        txt = 'Trop lent!'
    else:
        txt = 'Too slow!'
    feedback_map = {
        'NA': (txt, "red", False, 0),
        0: ("Correct!\n+ 3pt", "green", True, 3),
    }
    return feedback_map.get(distance, ("Incorrect!\n+ 0pt", "red", False, 0))

def get_trial_feedback(n_points:int, max_points:int, lang:str)-> str:
    '''Return the feedback text based on the number of points obtained'''
    messages = {
        'en': [
            (0, f"Too bad! You didn't win any points out of {max_points}."),
            (0.4, f"Not bad, you won {n_points} points out of {max_points}. Keep trying!"),
            (0.7, f"Well done! You got {n_points} points out of {max_points}."),
            (1.0, f"Excellent! You almost made it with {n_points} points out of {max_points}."),
            (1.0, f"Bravo! Perfect score: {n_points} out of {max_points} !")
        ],
        'fr': [
            (0, f"Dommage! Vous n'avez gagné aucun point sur {max_points}."),
            (0.4, f"Pas mal, vous avez gagné {n_points} points sur {max_points}. Continuez à essayer !"),
            (0.7, f"Bien joué! Vous avez obtenu {n_points} points sur {max_points}."),
            (1.0, f"Excellent! Vous avez presque réussi avec {n_points} points sur {max_points}."),
            (1.0, f"Bravo! Score parfait : {n_points} sur {max_points} !")
        ]
    }
    lang = lang if lang in messages else 'fr'  # default french
    score_ratio = n_points / max_points if max_points > 0 else 0
    for threshold, message in messages[lang]:
        if score_ratio <= threshold:
            return message

    return messages[lang][-1][1] # if issue, return the last message

def get_reward_sound(reward_sounds, n_points:int):
    ''' Return the reward sound (psychopy.sound) based on the number of points obtained for this question.'''
    if n_points < 3:
        return None
    elif n_points == 3:
        return reward_sounds[2]
    else:
        raise ValueError(f"Invalid number of points: {n_points}")

def run_question(tools:dict, slots:dict, start_item, end_item, rt_clock, global_clock, t_act:float, key_dict:dict)-> Tuple[int, float]:
    '''Run a question where the participant has to place the second item in the correct position.
    NB : it adds 1 to the returned index to takes into account the first item of the sequence (which is not
    selectable)'''

    demo = False # added after the demo was implemented
    if 'demo' in tools:
        demo = True

    left_key = key_dict['left_key']
    right_key = key_dict['right_key']
    confirm_key = key_dict['confirm_key']
    wait_fun = tools['wait_fun']
    event_fun = tools['event_fun']
    clear_event_fun = tools['clear_event_fun']
    if not demo:
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

    iterations = 0
    current_index = 0
    highlight_onset = None
    running = True
    global_clock.reset()
    rt_clock.reset()

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

            if left_key in keys:
                current_index = move_highlight(slots, current_index=current_index, direction="left")
                if not demo:
                    trig_fun(current_index+101) # WARNING what is this?
                    tools['logger'].info(f"Left key pressed, current index: {current_index+1}")

            if right_key in keys:
                current_index = move_highlight(slots, current_index=current_index, direction="right")
                if not demo:
                    # should there be a trigger here?
                    tools['logger'].info(f"Right key pressed, current index: {current_index+1}")

            if confirm_key in keys:
                if not demo:
                    trig_fun(current_index+101) # trigger is the slot index + 101 TODO: change this to something adaptive
                resp_time = rt_clock.getTime()
                global_clock.reset() # reset the global clock to avoid time out
                reset_highlight(slots)
                end_item.pos = slots[current_index]["rect"].pos # move the end item to the selected slot
                draw_all()
                tools['win'].flip()
                if not demo:
                    tools['logger'].info('Space key pressed')
                    tools['logger'].info(f'Index selected: {current_index+1}')
                    tools['logger'].info(f'RT: {resp_time}')
                wait_fun(1)
                running = False

            if "escape" in keys:
                running = False

            if global_clock.getTime() > t_act:
                if not demo:
                    trig_fun(200) 
                    tools['logger'].info('Time out')
                    tools['logger'].info(f'clock time: {global_clock.getTime()}')
                running = False
                resp_time = 'NA'
                reset_highlight(slots)
        
        iterations += 1

    return current_index+1, resp_time

def move_highlight(slots:dict, current_index:int, direction:bool=None)-> int:
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
        elif current_index == 0:
            current_index = current_index # removed the possibility to jump from position 1 to 5 
        else:
            current_index = len(slots) - 1
    elif direction == "right":
        if current_index < len(slots) - 1:
            current_index += 1
        else:
            current_index = current_index # removed the possibility to jump from position 5 to 1
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

# was used when I needed to distribute 2*6 sequences. Current version works for 12 unique sequences. 
def old_generate_run_org(input_dir, seq_structures) -> dict:
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
