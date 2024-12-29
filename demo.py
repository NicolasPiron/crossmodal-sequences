import os
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import numpy as np
import pandas as pd
from src import stimuli_manager as sm
from src import flow as fl
import src.params as pm


def run_demo():

    exp_info = {'ID': '00',
                'run': '01',
                'sequences': 'ABC',
                'nseq': 6,
                'order': 'fixed',
                'start modality': 'txt',
                'only questions': 'yes'
    }

    # run the experiment
    dlg = DlgFromDict(exp_info, title='Enter demo parameters', sortKeys=False)
    fl.handle_user_cancel(dlg)
    fl.check_demo_info(exp_info)

    out_dir = f"data/output/demo"
    os.makedirs(out_dir, exist_ok=True)
    if len(os.listdir(out_dir)) > 0:
        os.system(f"rm -r {out_dir}/*") # remove all files in the output directory

    sound_correct = sound.Sound(pm.sound_fn) # load sound here
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

    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
    seq1_name, seq2_name, seq3_name = exp_info['sequences']

    data = []
   
    for i in range(pm.n_blocks_demo): 
    
        block_id = i + 1
        block_info = visual.TextStim(win=win,
                        text=f'Block {block_id} \nAppuyez sur la touche ESPACE pour commencer!',
                        pos=(0, 0),
                        font="Arial",
                        color='black', 
                        height=pm.text_height,
                        units='norm')
        
        background.draw()
        block_info.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for j in range(pm.n_trials_demo): # 3 trials for a block

            trial_id = j + 1
            _, block_seq_org = sm.generate_block_org(block_modalities=['img', 'txt'],
                                                                sequences=[seq1_name, seq2_name, seq3_name])
            if exp_info['start modality'] == 'img':
                block_mod_org = ['img', 'txt']*3
            else:
                block_mod_org = ['txt', 'img']*3

            if exp_info['order'] == 'random':
                block_seq_org = block_seq_org
            elif exp_info['order'] == 'fixed':
                block_seq_org = [seq1_name, seq2_name, seq3_name]*2
            
            print(f"Block {block_mod_org}, seq {block_seq_org}")
            for k, modality in enumerate(block_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
                
                if k + 1 > int(exp_info['nseq']):
                    continue

                sequence_name = block_seq_org[k]
                sequence = amodal_sequences[sequence_name]
                stims = sm.get_stims(pm.input_dir, sequence, modality)

                for stim in stims:
                    if exp_info['only questions'] == 'yes':
                                continue
                        
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
            for l, seq_name in enumerate(block_seq_org[0:3]):

                question_id = l + 1 
            
                fl.check_escape(win)

                seq = amodal_sequences[seq_name] # get the sequence of items
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
                
                rt_clock = core.Clock()
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
                win.callOnFlip(rt_clock.reset) # TODO: do we want the reset when the image starts to appear or when it's fully visible?
                win.flip()

                fl.check_escape(win)
                resp = event.waitKeys(keyList=['left', 'right'], timeStamped=rt_clock, maxWait=10)

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
                    sound_correct.play()
                core.wait(1)
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data.append({'ID': exp_info['ID'],
                            'run': exp_info['run'],
                            'date': date,
                            'block': block_id,
                            'trial': trial_id,
                            'question': question_id,
                            'modality': modality,
                            'sequence_name': seq_name,
                            'first_presented': seq[first_presented],
                            'second_presented': seq[second_presented],
                            'correct_answer': correct_answer,
                            'response': key,
                            'correct': correct,
                            'rt': rt})
                
                pd.DataFrame(data).to_csv(f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}.csv", index=False)


if __name__ == "__main__":
    run_demo()
