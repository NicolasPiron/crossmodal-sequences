from psychopy import prefs
#import pickle

# paths
input_dir = "data/input"
output_dir = "data/output"
bg_fn = f"{input_dir}/background/background2.jpg"
stim_bg_fn = f"{input_dir}/background/stim_bg.png"
sound0_fn = f'{input_dir}/sounds/reward.mp3'
instr_fn = f"{input_dir}/instructions/instructions.txt"
instr_stimpres_fn = f"{input_dir}/instructions/instr_stim_pres.txt"
fix_img_fn = f"{input_dir}/fix/fix.png"
q_reward_fn = [f'{input_dir}/sounds/reward{i}.mp3' for i in range(1, 4)]

# stim config
t = 0.00001 # speed of text presentation
screen = 0 
seed = 42
bg_color = (255, 255, 255)
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
isi_dur = 1.5
stim_dur = 0.5
jitter = 0.2
prefs.hardware['audioLib'] = ['PTB']
use_mock_port = True
pport = None
categories = {
    'animals':0,
    'bodyparts':1,
    'characters':2,
    'colors':3,
    'landscapes':4,
    'shapes':5,
}

# organization
n_amodal_items_per_cat = 6
n_blocks = 4
n_trials = 3
n_blocks_demo = 1
n_trials_demo = 1

seq_structures = {
    'A': [1, 4, 2, 5, 0, 3],
    'B': [4, 5, 1, 3, 2, 0],
    'C': [5, 3, 4, 0, 1, 2],
    'D': [0, 2, 3, 1, 5, 4],
    'E': [3, 0, 5, 2, 4, 1],
    'F': [2, 1, 0, 4, 3, 5]
}
# cleaner way instead of hardcoding
# seq_structures = pickle.load(open(f"{input_dir}/seq_structures/seq_structures.pkl", "rb"))

# params for the in-task questions
viz_t = 5
act_t = 5
q_img_size = 0.2
q_slot_size = q_img_size + 0.001
hl_size = q_slot_size + 0.001
y_pos = 0.25
max_points = 9

# params for additional_q.py
bq_img_size = 0.1
bq_hl_size = bq_img_size + 0.001

triggers = {
    'animals':{
        'img':{
            'seq':1,
            'quest':11},
        'txt':{
            'seq':101,
            'quest':111}
    }, 
    'bodyparts':{
        'img':{
            'seq':2,
            'quest':12},
        'txt':{
            'seq':102,
            'quest':112}
    },
    'characters':{
        'img':{
            'seq':3,
            'quest':13},
        'txt':{
            'seq':103,
            'quest':113}
    },
    'colors':{
        'img':{
            'seq':4,
            'quest':14},
        'txt':{
            'seq':104,
            'quest':114}
    },
    'landscapes':{
        'img':{
            'seq':5,
            'quest':15},
        'txt':{
            'seq':105,
            'quest':115}
    },
    'shapes':{
        'img':{
            'seq':6,
            'quest':16},
        'txt':{
            'seq':106,
            'quest':116}
    },
    'slot2':202,
    'slot3':203,
    'slot4':204,
    'slot5':205,
    'slot6':206,
    'time_out':200,
}