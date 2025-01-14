import os
import logging
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound, parallel
import numpy as np
import pandas as pd
from src import stimuli_manager as sm
from src import flow as fl
import src.params as pm
import byte_triggers as bt
from present_stims import present_stims

# WARNING : do not forget to set randomization to True when real subjects are tested. 

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

    bt.add_file_handler(logfn, mode='a', verbose='INFO')
    logging.basicConfig(
        filename=logfn,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if pm.use_mock_port:
        pport = bt.MockTrigger()
    else:
        pport = bt.ParallelPortTrigger(pm.pport, delay=10)

    logger = logging.getLogger()
    logger.info('Experiment started.')
    logger.info(f'Participant ID: {exp_info["ID"]}')
    logger.info(f'Run number: {exp_info["run"]}')

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
    logger.info('Instructions successfully presented.')

    # Generate the multimodal sequences of items
    try:
        sm.check_nstims(pm.categories, pm.input_dir)
        sm.check_img_txt(pm.input_dir)
        amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, randomize=False) # False for testing purposes
        run_org = sm.distribute_sequences_block(sequences=amodal_sequences, n_blocks=pm.n_blocks)
        logger.info('Sequences successfully generated.')
        logger.info('sequences: ' + str(amodal_sequences))
        logger.info('run organization: ' + str(run_org))
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, win)

    data = [] # data store for responses

    try:
        for i in range(pm.n_blocks): # 4 blocks in a run

            try:
                block_id = i + 1

                items_used_for_questions = {} # this is initialized at the beginning of each block to avoid repetitions

                chosen_sequences = run_org[f'block{block_id}']
                logger.info(f'block: {block_id}')
                logger.info(f'sequences: {chosen_sequences}')

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

                # e.g. {'trial1': ['A', 'B', 'C', 'A', 'B', 'C'], 'trial2': ['C', 'A', 'B'...
                block_org = sm.distribute_sequences_trial(sequence_names=chosen_sequences, n_trials=pm.n_trials)
                logger.info(f'block organization: {block_org}')

                for j in range(pm.n_trials): # 3 trials for a block

                    trial_id = j + 1
                    trial_seq_org = block_org[f'trial{trial_id}'] # e.g. ['A', 'B', 'C', 'A', 'B', 'C']
                    trial_mod_org = sm.generate_modalities(start_with_img=False) # e.g. ['img', 'txt', 'img', 'txt', 'img', 'txt']

                    logger.info(f'trial: {trial_id}')
                    logger.info('block modalities order: ' + str(trial_mod_org))
                    logger.info('block sequences order: ' + str(trial_seq_org))

                    for k, modality in enumerate(trial_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
                        
                        sequence_name = trial_seq_org[k]
                        sequence = amodal_sequences[sequence_name]
                        stims = sm.get_stims(pm.input_dir, sequence, modality)

                        logger.info(f'sequence number: {k+1}')
                        logger.info(f'sequence name: {sequence_name}')
                        logger.info(f'sequence modality: {modality}')

                        for l, stim in enumerate(stims):
                            
                            if debugging:
                                continue

                            stim_cat = sm.get_cat_from_stim(stim)
                            trig = pm.triggers[stim_cat]['seq']
                        
                            fl.check_escape(win, logger)
                            stim_image = visual.ImageStim(win=win,
                                                            image=stim,
                                                            size=(pm.img_size, pm.img_size*aspect_ratio))
                                                    
                            background.draw()
                            stim_image.draw()
                            # log info there to be closer to the actual presentation
                            logger.info(f'stimulus number: {l+1}')
                            logger.info(f'stimulus name: {str(sequence[l])}')
                            logger.info(f'stimulus category: {stim_cat}')
                            logger.info(f'stimulus path: {stim}')

                            win.callOnFlip(pport.signal, trig)
                            win.flip()

                            if debugging:
                                core.wait(0.3)
                            else:
                                core.wait(pm.stim_dur + sm.jitter_isi(pm.jitter))

                            # Display fixation cross
                            fix_cross = visual.TextStim(win=win,
                                                            text='+',
                                                            font='Arial',
                                                            height=0.1,
                                                            color='black',
                                                            units='norm')
                            background.draw()
                            fix_cross.draw()
                            win.flip()
                            if debugging:
                                core.wait(0.5)
                            else:
                                core.wait(pm.isi_dur)
                                                    
                    # Ask questions. 3 questions, one for each amodal sequence. 
                    good_answers_count = 0
                    for l, seq_name in enumerate(trial_seq_org[0:3]):

                        question_id = l + 1 
        
                        logger.info(f'question number: {question_id}')
                        logger.info(f'sequence name: {seq_name}')
                        fl.check_escape(win, logger)

                        sequence = amodal_sequences[seq_name] # redefine the sequence to be used for the question
                        if seq_name in items_used_for_questions: # check if the items used for the question have already been used
                            ignore_idx = items_used_for_questions[seq_name]
                        else:
                            ignore_idx = None
                        idx1, idx2 = sm.draw_two(sequence, ignore_idx=ignore_idx) # draw two items from the sequence (e.g. (0, 4))

                        first_for_question = sequence[idx1] # first item to be presented for the question (e.g. 'cow')
                        second_for_question = sequence[idx2]
                        first_in_seq = sequence[np.min([idx1, idx2])] # good answer as a string (e.g. 'cow')

                        if seq_name in items_used_for_questions: # store idx of items used for this sequence
                            items_used_for_questions[seq_name].extend([idx1, idx2])
                        else:
                            items_used_for_questions[seq_name] = [idx1, idx2]

                        if first_in_seq == first_for_question:
                            correct_answer = 'left'
                            wrong_answer = 'right'
                        elif first_in_seq == second_for_question:
                            correct_answer = 'right'
                            wrong_answer = 'left'

                        # randomly select in which modality the question will be asked
                        modality = np.random.choice(['img', 'txt'])
                        stims = sm.get_stims(pm.input_dir, sequence, modality)

                        cat1 = sm.get_cat_from_stim(stims[idx1])
                        cat2 = sm.get_cat_from_stim(stims[idx2])
                        trig1 = pm.triggers[cat1]['quest']
                        trig2 = pm.triggers[cat2]['quest']

                        stim1 = visual.ImageStim(win=win,
                                                image=stims[idx1],
                                                pos=(-0.4, 0),
                                                size=(pm.img_size, pm.img_size*aspect_ratio),
                                                units='norm')
                        stim2 = visual.ImageStim(win=win,
                                                image=stims[idx2],
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
                        
                        question_clock = core.Clock() # maybe useless
                        rt_clock = core.Clock()

                        logger.info(f'first item on screen: {first_for_question}')
                        logger.info(f"first item's index: {idx1}")
                        logger.info(f"first item's category: {cat1}")
                        
                        # for opacity in range(0, 101, 5): # Fading-in effect, REMOVED for now?
                        #     background.draw()
                        #     stim1.opacity = opacity / 100
                        #     stim1.draw()
                        #     q_high.draw()
                        #     arrow_l.draw()
                        #     arrow_r.draw()
                        #     win.flip()
                        #     core.wait(0.01)
                        
                        stim1.opacity = 1 # do it again to make sure the clock has reset for the last flip
                        background.draw()
                        stim1.draw()
                        q_high.draw()
                        arrow_l.draw()
                        arrow_r.draw()
                        win.callOnFlip(pport.signal, trig1)
                        win.callOnFlip(question_clock.reset) # TODO: do we want the reset when the image starts to appear or when it's fully visible?
                        win.flip()

                        if debugging:
                            wait_2nd_stim = 0
                        else:
                            wait_2nd_stim = 5
                        core.wait(wait_2nd_stim) # justify 5s

                        logger.info(f'second item on screen: {second_for_question}')
                        logger.info(f"second item's index: {idx2}")
                        logger.info(f"second item's category: {cat2}")

                        background.draw()
                        stim1.draw()
                        stim2.draw()
                        q_high.draw()
                        arrow_l.draw()
                        arrow_r.draw()
                        win.callOnFlip(pport.signal, trig2)
                        win.callOnFlip(rt_clock.reset)
                        win.flip()

                        logger.info(f"correct answer: {correct_answer}")
                        
                        fl.check_escape(win, logger)
                        resp = event.waitKeys(keyList=['left', 'right'], timeStamped=rt_clock, maxWait=10)

                        if resp is None:
                            pport.signal(pm.triggers['incorrect'])
                            key = 'NA'
                            rt = 'NA'
                            correct = False
                            feedback_text = "Trop lent!"
                            font_color = 'red'
                        else:
                            key = resp[0][0]
                            rt = resp[0][1]
                            if key == correct_answer:
                                pport.signal(pm.triggers['correct'])
                                correct = True
                                feedback_text = "Correct!"
                                font_color = 'green'
                                good_answers_count += 1
                            elif key == wrong_answer:
                                pport.signal(pm.triggers['incorrect'])
                                correct = False
                                feedback_text = "Incorrect!"
                                font_color = 'red'

                        logger.info(f'key pressed: {key}')
                        logger.info(f'correct response: {correct}')
                        logger.info(f'RT: {rt}')

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
                                    'first_presented': first_for_question,
                                    'second_presented': second_for_question,
                                    'correct_answer': correct_answer,
                                    'response': key,
                                    'correct': correct,
                                    'rt': rt})

                        pd.DataFrame(data).to_csv(f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}.csv", index=False)
                        core.wait(0.5)
                    
                    # encouraging message
                    if good_answers_count == 3:
                        reward_max.play() 
                    trial_feedback = pm.trial_feedback[good_answers_count]

                    if trial_id == 3:
                        block_info = f"Fin du bloc {block_id}. Le bloc suivant va commencer."
                    else:
                        block_info = f"L'essai suivant va commencer."

                    fl.type_text(f"{trial_feedback} \n{block_info}",
                                win,
                                height=pm.text_height,
                                background=background,
                                t=pm.t)
                    if debugging:
                        core.wait(0.1)
                    else:
                        core.wait(3)

                logger.info(f'Block {block_id} completed successfully.')
                logger.info('========== End of block ==========')
            except Exception as exc:
                fl.log_exceptions(f"Error during run {exp_info['run']}, block {block_id}: {exc}", logger, win)

        logger.info(f'Run {exp_info["run"]} completed successfully.')
        logger.info('=============== End of run ===============')
        win.close()
        core.quit()

    except Exception as exc:
        fl.log_exceptions(f"An error occurred during the run {exp_info['run']}: {exc}", logger, win)

if __name__ == '__main__':
    #present_stims()
    run(debugging=False)
    #run() 