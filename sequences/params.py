from psychopy import prefs
from pathlib import Path
import platform

os_name = platform.system()
# paths
input_dir = Path("data/input")
output_dir = Path("data/output")
bg_fn = Path(f"{input_dir}/background/background2.jpg")
stim_bg_fn = Path(f"{input_dir}/background/stim_bg.png")
sound0_fn = Path(f'{input_dir}/sounds/reward.mp3')
fix_img_fn = Path(f"{input_dir}/fix/fix.png")
q_reward_fn = [Path(f'{input_dir}/sounds/reward{i}.mp3') for i in range(1, 4)]
instr_fnames = {
    'instr1_fn': 'instructions_p1.txt',
    'instr2_fn' : 'instructions_p2.txt',
    'instr_q_fn' : 'instructions_q.txt',
    'instr_bonus_fn' : 'instructions_bonus.txt',
    'instr_bonus2_fn' : 'instructions_bonus2.txt',
    'instr_bonus3_fn' : 'instructions_bonus3.txt',
    'instr_stimpres_fn' : 'instr_stim_pres.txt',
    'instr_stimpres2_fn' : 'instr_stim_pres2.txt',
    'instr_stimpres3_fn' : 'instr_stim_pres3.txt',
}
key_dict = {
    'left_key' : '1',
    'confirm_key' : '2',
    'right_key' : '3',
    'pause_key' : '4', 
}

# stim config
t = 0.001 # speed of text presentation
#seed = 42
bg_color = (255, 255, 255)
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
isi_dur = 1.5
stim_dur = 0.5
jitter = 0.2 # TODO: change to shorter value
prefs.hardware['audioLib'] = ['PTB']
if os_name == "Windows":
    screen = 1
    use_mock_port = False
    pport = 0x2FB8
elif os_name == "Linux":
    screen = 1
    use_mock_port = False
    pport = ''
elif os_name == "Darwin":
    screen = 0
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
n_seq = 6
n_blocks_demo = 1
n_trials_demo = 1

# seq_structures = {
#     'A': [1, 4, 2, 5, 0, 3],
#     'B': [4, 5, 1, 3, 2, 0],
#     'C': [5, 3, 4, 0, 1, 2],
#     'D': [0, 2, 3, 1, 5, 4],
#     'E': [3, 0, 5, 2, 4, 1],
#     'F': [2, 1, 0, 4, 3, 5]
# }

seq_structures = {
    'A': [1, 0, 5, 3, 2, 4],
    'B': [0, 2, 1, 4, 3, 5],
    'C': [1, 3, 0, 2, 4, 5],
    'D': [5, 1, 4, 0, 2, 3],
    'E': [4, 3, 2, 5, 1, 0],
    'F': [2, 0, 3, 1, 5, 4],
    'G': [3, 4, 0, 5, 1, 2],
    'H': [4, 2, 1, 0, 3, 5],
    'I': [2, 1, 3, 4, 5, 0],
    'J': [5, 4, 2, 3, 0, 1],
    'K': [3, 5, 2, 4, 0, 1],
    'L': [5, 0, 4, 3, 1, 2],
}


# params for the in-task questions
t_prep = 2
t_viz_cue = 5
t_viz_target = 3
t_act = 2
t_fb = 1
t_iqi = 0.5
t_post_q = 3
t_post_block = 30 # To adjust after discussion
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