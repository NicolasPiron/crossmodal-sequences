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
screen = 0 
seed = 42
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
iti_dur = 1.5
stim_dur = 0.5
prefs.hardware['audioLib'] = ['PTB']

# organization
n_amodal_items_per_cat = 6
n_blocks = 4
n_trials = 3
n_blocks_demo = 1
n_trials_demo = 1

seq_structures = {'A': [0, 1, 2, 3, 4, 5],
                'B': [2, 4, 5, 1, 0, 3],
                'C': [1, 4, 2, 0, 3, 5],
                'D': [3, 0, 1, 5, 2, 4],
                'E': [4, 1, 0, 5, 3, 2],
                'F': [5, 2, 3, 4, 1, 0]
}

run_structure = {

}

cat_mapping = {0:'colors',
               1:'shapes',
               2:'animals',
               3:'landscapes',
               4:'characters',
               5:'bodyparts',
}