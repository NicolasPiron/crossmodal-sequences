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
    'instr_pause_fn': 'instr_pause.txt', 
    'instr_reward_fn': 'instr_reward.txt',
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
stim_dur = 0.3 # 0.55s in the data. 
jitter = 0.2 # TODO: change to shorter value
prefs.hardware['audioLib'] = ['PTB']
if os_name == "Windows":
    screen = 1
    use_mock_port = False
    pport = 0x2FB8
elif os_name == "Linux":
    screen = 0
    use_mock_port = False
    pport = '/dev/parport0'
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
# TODO: maybe use frame rate to calculate the time
t_prep = 2
t_viz_cue = 5
t_viz_target = 3
t_act = 2
t_fb = 1
t_iqi = 0.5
t_post_q = 3
t_post_block = 30 # To adjust after discussion
t_post_run = 1
q_img_size = 0.2
q_slot_size = q_img_size + 0.001
hl_size = q_slot_size + 0.001
y_pos = 0.25
max_points = 9

# for rewarded sequence presentation
rw_img_size = 0.2
rw_hl_size = rw_img_size + 0.025
# rw_hl_color = (212, 175, 55) # gold
rw_hl_color = '#D4AF37'
flick_freq = 1 # Hz
t_reward_info = 15

# params for additional_q.py
bq_img_size = 0.1
bq_hl_size = bq_img_size + 0.001

# trigger mapping :
# - trig1 : sequence + position -> between 11 and 126
# - trig2 : category + modality -> between ...

trig1 = {
    'A':[11, 12, 13, 14, 15, 16],
    'B':[21, 22, 23, 24, 25, 26],
    'C':[31, 32, 33, 34, 35, 36],
    'D': [41, 42, 43, 44, 45, 46],
    'E': [51, 52, 53, 54, 55, 56],
    'F': [61, 62, 63, 64, 65, 66],
    'G': [71, 72, 73, 74, 75, 76],
    'H': [81, 82, 83, 84, 85, 86],
    'I': [91, 92, 93, 94, 95, 96],
    'J': [101, 102, 103, 104, 105, 106],
    'K': [111, 112, 113, 114, 115, 116],
    'L': [121, 122, 123, 124, 125, 126],
}

trig2 = {
    'img': {
        'animals': 131,
        'bodyparts': 132,
        'characters': 133,
        'colors': 134,
        'landscapes': 135,
        'shapes': 136,
    },
    'txt': {
        'animals': 241,
        'bodyparts': 242,
        'characters': 243,
        'colors': 244,
        'landscapes': 245,
        'shapes': 246,
    },
}

trig3 = {
    'left': 201,
    'right': 202,
    'confirm': 203,
    'fb_correct': 204,
    'fb_incorrect': 205, 
    'timeout': 206,
    'block_pause': 207,
    'block_endpause': 208,
    'run_pause': 209,
    'run_endpause': 210,
    'reward_info': 211,
}

triggers = {
    'seq_pos': trig1,
    'mod_cat':trig2,
    'misc': trig3,
}