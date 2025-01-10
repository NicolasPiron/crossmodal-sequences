from psychopy import prefs

# paths
input_dir = "data/input"
bg_fn = f"{input_dir}/background/background2.jpg"
stim_bg_fn = f"{input_dir}/background/stim_bg.png"
sound0_fn = f'{input_dir}/sounds/reward.mp3'
sound1_fn = f'{input_dir}/sounds/reward1.mp3'
sound2_fn = f'{input_dir}/sounds/reward2.mp3'
sound3_fn = f'{input_dir}/sounds/reward3.mp3'
instr_fn = f"{input_dir}/instructions/instructions.txt"
instr_stimpres_fn = f"{input_dir}/instructions/instr_stim_pres.txt"
fix_img_fn = f"{input_dir}/fix/fix.png"

# stim config
t = 0.00001 # speed of text presentation
screen = 0 
seed = 42
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
iti_dur = 1.5
stim_dur = 0.5
prefs.hardware['audioLib'] = ['PTB']
use_mock_port = True
pport = None
categories = {'animals':0,
                'bodyparts':1,
                'characters':2,
                'colors':3,
                'landscapes':4,
                'shapes':5,
    }

triggers = {'animals':{'seq':1, 'quest':11}, # TODO: add more triggers (modalities etc.)
                'bodyparts':{'seq':2, 'quest':12},
                'characters':{'seq':3, 'quest':13},
                'colors':{'seq':4, 'quest':14},
                'landscapes':{'seq':5, 'quest':15},
                'shapes':{'seq':6, 'quest':16},
                'correct':101,
                'incorrect':102,
    }

# organization
n_amodal_items_per_cat = 6
n_blocks = 4
n_trials = 3
n_blocks_demo = 1
n_trials_demo = 1

seq_structures = {'A': [1, 4, 2, 5, 0, 3],
                'B': [4, 5, 1, 3, 2, 0],
                'C': [5, 3, 4, 0, 1, 2],
                'D': [0, 2, 3, 1, 5, 4],
                'E': [3, 0, 5, 2, 4, 1],
                'F': [2, 1, 0, 4, 3, 5]
}
