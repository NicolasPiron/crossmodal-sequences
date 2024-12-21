from psychopy import sound
import glob

cat_mapping = {0:'colors',
               1:'shapes',
               2:'animals',
               3:'landscapes',
               4:'characters',
               5:'bodyparts',
}

seq_structures = {'A':[0, 1, 2, 3, 4, 5],
             'B':[3, 1, 4, 0, 5, 2],
             'C':[5, 3, 2, 0, 4, 1],
}

screen = 0 
seed = 42
text_height = 0.08
img_size = 0.4
img_bg_size = 0.41
win_size = [1512, 982]
iti_dur = 1.5
stim_dur = 0.5
input_dir = "data/input"
bg_fn = f"{input_dir}/background/background2.jpg"
stim_bg_fn = f"{input_dir}/background/stim_bg.png"
sound_correct = sound.Sound(f'{input_dir}/sounds/reward.mp3')
instr_fn = f"{input_dir}/instructions/instructions.txt"
instr_stimpres_fn = f"{input_dir}/instructions/instr_stim_pres.txt"
fix_img_fn = f"{input_dir}/fix/fix.png"
n_amodal_items_per_cat = int(len(glob.glob(f"{input_dir}/stims/animals/*.png"))/2)