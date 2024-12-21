from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import numpy as np
import pandas as pd
import os
import glob
from src import stimuli_manager as sm
from src import flow as fl
import src.params as pm
from present_stims import present_stims

#present_stims()

# parameters

exp_info = {'ID': '00',
            'run': '01',
}

# run the experiment

dlg = DlgFromDict(exp_info, title='Enter participant info', sortKeys=False)
fl.handle_user_cancel(dlg)
fl.check_user_info(exp_info)

out_dir = f"data/output/sub-{exp_info['ID']}"
logfn = f"{out_dir}/info.log"

os.makedirs(out_dir, exist_ok=True)
if os.path.isfile(logfn):
    raise ValueError("File already exists.")

# Create a window
win = visual.Window(size=pm.win_size,
                    fullscr=True,
                    units='norm', 
                    screen=pm.screen,)
win.mouseVisible = False
aspect_ratio = win.size[0] / win.size[1]

# Create the background image
background = visual.ImageStim(
    win, 
    size=(2, 2*aspect_ratio),
    image=pm.bg_fn, 
    units="norm"
)

# Initialization
fl.type_text("Nous allons présenter les instructions.\nAppuyez sur la touche ESPACE pour continuer.",
            win,
            height=pm.text_height,
            background=background)

event.waitKeys(keyList=['space'])

with open(pm.instr_fn, "r", encoding="utf-8") as file:
    instructions_text = file.read()

instructions = visual.TextStim(
    win, text=instructions_text, font="Arial", color='black',  height=pm.text_height,
    alignText="center" )

background.draw()
instructions.draw()
win.flip()

fl.check_escape(win)
event.waitKeys(keyList=['space'])

# Generate the multimodal sequences of items
sm.check_nstims(pm.cat_mapping, pm.input_dir)
amodal_sequences = sm.generate_sequences(pm.n_amodal_items_per_cat, pm.cat_mapping, pm.input_dir)
amodal_sequences = sm.reorg_seq(amodal_sequences, pm.seq_structures) # TODO: save the used items somewhere so they are not used again. 

data = []

for i in range(3): # 3 * mini-blocks (or trials) for a block

    # define trial number here for clarity
    trial = i + 1

    # Generate random order of modalities and sequence types for a block
    block_mod_org, block_seq_types_org = sm.generate_block_org(block_modalities=['img', 'txt'],
                                                        block_seq_types=['A', 'B', 'C'])

    for j, modality in enumerate(block_mod_org): # loop over the 6 sequences (A, B, C * the two modalities (img, txt))

        sequence_type = block_seq_types_org[j]
        sequence = amodal_sequences[sequence_type]
        stims = sm.get_stims(pm.input_dir, sequence, modality)

        for stim in stims:
        
            fl.check_escape(win)
            stim_image = visual.ImageStim(win=win,
                                            image=stim,
                                            size=(pm.img_size, pm.img_size*aspect_ratio))
                                     
            background.draw()
            stim_image.draw()
            win.flip()
            core.wait(pm.stim_dur)
            # Display fixation cross
            fix_image = visual.TextStim(win=win,
                                            text='+',
                                            font='Arial',
                                            height=0.1,
                                            color='black',
                                            units='norm')
            background.draw()
            fix_image.draw()
            win.flip()
            core.wait(pm.iti_dur)
                                     
    # Ask questions. 3 questions, one for each amodal sequence. 
    for k, seq_type in enumerate(block_seq_types_org[0:3]):

        fl.check_escape(win)
        question_nr = k + 1 # question number defined here for clarity

        seq = amodal_sequences[seq_type] # get the sequence of items
        idx1, idx2 = sm.draw_two(seq) # draw two items from the sequence
        first_presented = np.min([idx1, idx2])
        second_presented = np.max([idx1, idx2])
        correct_answer = seq[first_presented] # good answer as a string

        # randomly select in which modality the question will be asked
        modality = np.random.choice(['img', 'txt'])
        stims = sm.get_stims(pm.input_dir, seq, modality)
        stim1 = visual.ImageStim(win=win,
                                image=stims[first_presented],
                                pos=(-0.4, 0),
                                size=(pm.img_size, pm.img_size*aspect_ratio),
                                units='norm')
        stim2 = visual.ImageStim(win=win,
                                image=stims[second_presented],
                                pos=(0.4, 0),
                                size=(pm.img_size, pm.img_size*aspect_ratio),
                                units='norm')

        text_q_high = 'Quel item arrive en premier dans la séquence? \n Utilisez les flèches du clavier pour répondre.'
        text_al = '<-'
        text_ar = '->'
        
        q_high = visual.TextStim(win=win, text=text_q_high, pos=(0, 0.55), height=pm.text_height,
                                    color='black', units='norm')
        arrow_l = visual.TextStim(win=win, text=text_al, pos=(-0.4, -0.45), height=pm.text_height,
                                    color='black', units='norm')
        arrow_r = visual.TextStim(win=win, text=text_ar, pos=(0.4, -0.45), height=pm.text_height,
                                    color='black', units='norm')
        
        clock = core.Clock()
        for opacity in range(0, 101, 5): # Fading-in effect
            background.draw()
            stim1.opacity = opacity / 100
            stim2.opacity = opacity / 100
            stim1.draw()
            stim2.draw()
            q_high.draw()
            arrow_l.draw()
            arrow_r.draw()
            win.flip()
            core.wait(0.01)
        
        stim1.opacity = 1 # do it again to make sure the clock has reset for the last flip
        stim2.opacity = 1
        background.draw()
        stim1.draw()
        stim2.draw()
        q_high.draw()
        arrow_l.draw()
        arrow_r.draw()
        win.callOnFlip(clock.reset)
        win.flip()

        fl.check_escape(win)
        resp = event.waitKeys(keyList=['left', 'right'], timeStamped=clock, maxWait=10)

        if resp is None:
            key = 'NA'
            rt = 'NA'
            correct = False
            feedback_text = "Trop lent!"
            font_color = 'red'
        else:
            key = resp[0][0]
            rt = resp[0][1]
        
        if (key == 'left' and first_presented == idx1) or (key == 'right' and first_presented == idx2):
            correct = True
            feedback_text = "Correct!"
            font_color = 'green'
        elif (key == 'left' and first_presented == idx2) or (key == 'right' and first_presented == idx1):
            correct = False
            feedback_text = "Incorrect!"
            font_color = 'red'

        feedback = visual.TextStim(win=win,
                                    text=feedback_text,
                                    pos=(0, 0),
                                    font="Arial",
                                    color=font_color, 
                                    height=pm.text_height,
                                    units='norm',
                                    bold=True)
        
        background.draw()
        feedback.draw()
        win.flip()
        if correct:
            pm.sound_correct.play()
        core.wait(1)

        data.append({'ID': exp_info['ID'],
                    'run': exp_info['run'],
                    'trial': trial,
                    'question': question_nr,
                    'modality': modality,
                    'sequence_type': seq_type,
                    'first_presented': seq[first_presented],
                    'second_presented': seq[second_presented],
                    'correct_answer': correct_answer,
                    'response': key,
                    'correct': correct,
                    'rt': rt})
        
        core.wait(0.5)

pd.DataFrame(data).to_csv(f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}.csv", index=False)

win.close()
core.quit()