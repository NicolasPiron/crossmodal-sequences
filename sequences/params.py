from psychopy import prefs
from pathlib import Path
import platform

os_name = platform.system()
# directories
input_dir = Path("data/input")
output_dir = Path("data/output")
spin_wheel_dir = Path(f"{input_dir}/spin_wheel")
snd_stim_dir = Path(f"{input_dir}/sounds/seq_sounds")
# file names
bg_fn = Path(f"{input_dir}/background/background3.jpg")
stim_bg_fn = Path(f"{input_dir}/background/stim_bg.png")
sound0_fn = Path(f'{input_dir}/sounds/reward.wav')
snd_endPause_fn = Path(f'{input_dir}/sounds/end_pause.wav')
fix_img_fn = Path(f"{input_dir}/fix/fix.png")
q_reward_fn = [Path(f'{input_dir}/sounds/reward{i}.wav') for i in range(1, 4)]
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
    'instr_tmr1': 'instr_tmr1.txt',
    'instr_tmr2': 'instr_tmr2.txt',
    'quest_ready_fn': 'quest_ready.txt',
    'quest_vigi_fn': 'quest_vigilance.txt',
    'quest_focus_fn': 'quest_focus.txt',
    'quest_think_fn': 'quest_think.txt',
}
# mapping of keys to numbers for the response pad
key_dict = {
    'left' : '1',
    'confirm' : '2',
    'right' : '3',
    'pause' : 'b',
    'up' : '4',
    'down' : '5',
}
# for the bonus question
key_bq = {
    'left':'1',
    'right':'3',
    'up':'8',
    'down':'9',
    'confirm':'2',
    'remove':'6',
}

# stim config
t = 0.001 # speed of text presentation
#seed = 42
frate = 120 
bg_color = (255, 255, 255)
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
prefs.hardware['audioLib'] = ['PTB']
if os_name == "Windows":
    screen = 1
    use_mock_port = False
    pport = 0x2FB8
elif os_name == "Linux":
    screen = 1
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

# sequence presentation timings
isi_dur = 1.5
stim_dur = 0.3 # + 50 ms in the actual presentation
jitter = 0.05 

# params for the in-task questions
# TODO: maybe use frame rate to calculate the time
t_prep = 2
t_viz_cue = 5
t_viz_target = 3
t_act = 2
t_fb = 1
t_iqi = 0.5
t_post_q = 5

q_img_size = 0.2
q_slot_size = q_img_size + 0.001
hl_size = q_slot_size + 0.001
y_pos = 0.25

max_points = 9

# for the questionnaire after each block
bar_c = '#254E70'
tick_c = '#254E70'
slider_c = 'white'
validation_c = '#AEF3E7'
slider_lc = 'black'
y_bar = -0.2
far_l = -0.5
far_r = 0.5
n_ticks = 7
bar_len = far_r - far_l
stxt_up = 0.2 
stxt_dict = {
    'fr': {
        'vigi':['somnolent.e', 'éveillé.e'],
        'focus': ['distrait.e', 'concentré.e'],
        'think': ['autre chose', 'séquences'],
    },
    'en': {
        'vigi': ['drowsy', 'awake'],
        'focus': ['distracted', 'focused'],
        'think': ['other things', 'sequences'],
    },
}
# end block pause
t_post_block = 30 # To adjust after discussion 30
t_rotate = 2 # seconds

# end of run pause
t_post_run = 90 # 90

# for rewarded sequence presentation
rw_img_size = 0.2
rw_hl_size = rw_img_size + 0.025
# rw_hl_color = (212, 175, 55) # gold
rw_hl_color = '#D4AF37'
flick_freq = 1 # Hz
t_reward_info = 10 # seconds

# params for the bonus question
bq_img_size = 0.1
bq_hl_size = bq_img_size + 0.001

# how much points rewarded (in chf)
reward_value = 0.5

# params for the TMR
t_tmr = 30
t_tmr_delay = 2
tmr_jitter = 1

# trigger mapping :
# - trig1 : sequence + position -> between 11 and 126
# - trig2 : category + modality -> between ...

trig1 = {
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

trig2 = {
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
    'tmr_A':221,
    'tmr_B':222,
    'tmr_C':223,
    'tmr_D':224,
    'tmr_E':225,
    'tmr_F':226,
    'tmr_G':227,
    'tmr_H':228,
    'tmr_I':229,
    'tmr_J':230,
    'tmr_K':231,
    'tmr_L':232,
}

triggers = {
    'mod_cat':trig1,
    'seq_pos': trig2,
    'misc': trig3,
}