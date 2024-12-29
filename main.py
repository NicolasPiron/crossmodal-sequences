import os
import logging
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import numpy as np
import pandas as pd
from src import stimuli_manager as sm
from src import flow as fl
import src.params as pm
from present_stims import present_stims

def run(debugging=False):

    exp_info = {'ID': '00',
                'run': '01',
    }

    # run the experiment
    dlg = DlgFromDict(exp_info, title='Enter participant info', sortKeys=False)
    fl.handle_user_cancel(dlg)
    fl.check_user_info(exp_info)

    out_dir = f"data/output/sub-{exp_info['ID']}"
    logfn = f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}_cmseq-logs-{datetime.now().strftime('%Y%m%d-%H%M')}.log"
    os.makedirs(out_dir, exist_ok=True)

    if len(os.listdir(out_dir)) > 0: # check if the output directory is empty to avoid overwriting data
        if not debugging:
            print(f"--- Output directory {out_dir} is not empty, exiting... ---")
            quit()
        else:
            os.system(f"rm -r {out_dir}/*") # remove all files in the output directory

    logging.basicConfig(
        filename=logfn,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger()

    reward_max = sound.Sound(pm.sound0_fn)
    reward1 = sound.Sound(pm.sound1_fn)
    reward2 = sound.Sound(pm.sound2_fn)
    reward3 = sound.Sound(pm.sound3_fn)

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
    if exp_info['run'] == '01': # only present the instructions at the first run
        fl.type_text("Nous allons présenter les instructions.\nAppuyez sur la touche ESPACE pour continuer.",
                    win,
                    height=pm.text_height,
                    background=background,
                    t=pm.t)
        event.waitKeys(keyList=['space'])

    with open(pm.instr_fn, "r", encoding="utf-8") as file:
        instructions_text = file.read()

    instructions = visual.TextStim(
        win, text=instructions_text, font="Arial", color='black',  height=pm.text_height,
        alignText="center" )

    background.draw()
    instructions.draw()
    win.flip()

    fl.check_escape(win, logger)
    event.waitKeys(keyList=['space'])

    # Generate the multimodal sequences of items
    try:
        sm.check_nstims(pm.cat_mapping, pm.input_dir)
        sm.check_img_txt(pm.input_dir)
        amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
        unique_sequences_pool = list(amodal_sequences.keys())*2 # to keep track of which sequences are sampled 
        logger.info('Sequences successfully generated.')
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, win)

    data = [] # data store for responses

    try:
        for i in range(pm.n_blocks): # 4 blocks in a run

            try:
                block_id = i + 1

                if block_id == 3:
                    # needs to be done at 3rd iteration so that the last block has 3 unique sequences
                    chosen_sequences, unique_sequences_pool = sm.sample_until_no_dupes(unique_sequences_pool) 
                else:
                    chosen_sequences, unique_sequences_pool = sm.sample_n_throw(unique_sequences_pool) # sample 3 sequences
                logger.info(f'Block {block_id} sequences: {chosen_sequences}')
                logger.info(f'Remaining unique_sequences_pool: {unique_sequences_pool}')

                block_info = visual.TextStim(win=win,
                                text=f'Bloc {block_id} \nAppuyez sur la touche ESPACE pour commencer!',
                                pos=(0, 0),
                                font="Arial",
                                color='black', 
                                height=pm.text_height,
                                units='norm')
                
                background.draw()
                block_info.draw()
                win.flip()
                event.waitKeys(keyList=['space'])

                for j in range(pm.n_trials): # 3 trials for a block

                    trial_id = j + 1

                    # Generate random order of modalities and sequence types for a block
                    block_mod_org, block_seq_org = sm.generate_block_org(block_modalities=['img', 'txt'],
                                                                        sequences=chosen_sequences)

                    for k, modality in enumerate(block_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
                        
                        logger.info(f'Block {block_id}, trial {trial_id}, sequence {k+1}...')
                        sequence_name = block_seq_org[k]
                        sequence = amodal_sequences[sequence_name]
                        stims = sm.get_stims(pm.input_dir, sequence, modality)

                        for stim in stims:

                            if debugging:
                                continue
                        
                            fl.check_escape(win, logger)
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
                    good_answers_count = 0
                    for l, seq_name in enumerate(block_seq_org[0:3]):

                        question_id = l + 1 
                        
                        logger.info(f'Block {block_id}, trial {trial_id}, question {question_id}...')
                        fl.check_escape(win, logger)

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

                        fl.check_escape(win, logger)
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
                            good_answers_count += 1
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
                        
                        # sound selection
                        if good_answers_count == 1:
                            reward = reward1
                        elif good_answers_count == 2:
                            reward = reward2
                        elif good_answers_count == 3:
                            reward = reward3
                        
                        background.draw()
                        feedback.draw()
                        win.flip()
                        if correct:
                            reward.play()
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
                        
                        logger.info(f'Saving data of trial {trial_id}, question {question_id}...')
                        pd.DataFrame(data).to_csv(f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}.csv", index=False)
                        logger.info('Data saved successfully.')
                        core.wait(0.5)
                    
                    # encouraging message
                    if good_answers_count == 3:
                        global_feedback = "Bravo! Vous avez répondu correctement à toutes les questions."
                        reward_max.play() 
                    elif good_answers_count == 2:
                        global_feedback = "Bien joué! Vous avez répondu correctement à 2 questions."
                    elif good_answers_count == 1:
                        global_feedback = "Pas mal! Vous avez répondu correctement à 1 question."
                    else:
                        global_feedback = "Dommage! Vous n'avez répondu correctement à aucune question."

                    if trial_id == 3:
                        block_info = f"Fin du bloc {block_id}. Le bloc suivant va commencer."
                    else:
                        block_info = f"L'essai suivant va commencer."

                    fl.type_text(f"{global_feedback} \n{block_info}",
                                win,
                                height=pm.text_height,
                                background=background,
                                t=pm.t)
                    core.wait(3)

                logger.info(f'Block {block_id} completed successfully.')
            except Exception as exc:
                fl.log_exceptions(f"Error during run {exp_info['run']}, block {block_id}: {exc}", logger, win)

        logger.info(f'Run {exp_info["run"]} completed successfully.')
        win.close()
        core.quit()

    except Exception as exc:
        fl.log_exceptions(f"An error occurred during the run {exp_info['run']}: {exc}", logger, win)

if __name__ == '__main__':
    #present_stims()
    run(debugging=True)
    #run()