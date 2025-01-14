import random
from typing import Dict, List



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
        for j, (img, txt) in enumerate(t_layout):
            block_org[f'block{i + 1}'][f'trial{j + 1}'] = ['img']*img + ['txt']*txt

    return block_org


def distribute_mod_seq(n_block)-> Dict[str, List[str]]:
    
    block_layouts = [(2, 1)] * 2 + [(1, 2)] * 2
    random.shuffle(block_layouts) # shuffle block layouts once
    block_org = {f'block{i + 1}': None for i in range(n_block)}
    for i, (img_count, txt_count) in enumerate(block_layouts):
        org = ['img']*img_count + ['txt']*txt_count
        random.shuffle(org)
        block_org[f'block{i + 1}'] = org
    return block_org


distribute_mod_seq(4)



