import os
import logging
import random
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import pandas as pd
from src import stimuli_manager as sm
from src import flow as fl
import src.params as pm
import byte_triggers as bt
from src.common import get_win_obj
from bonus_question import ask_all_seq
from dataclasses import dataclass
from typing import Callable

@dataclass
class Utils:
    debugging: bool
    pport: bt.MockTrigger  # CHANGE THIS TO bt.ParallelPortTrigger
    logger: logging.Logger
    win: visual.Window
    aspect_ratio: float
    background: visual.ImageStim
    wait_fun: Callable[[float], None]
    event_fun: Callable[[list], list]
    trig_fun: Callable[[int], None]

# WARNING : do not forget to set randomization to True when real subjects are tested. 

def run(debugging=False, ignore_q=False):

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
    q_reward_sounds = [sound.Sound(fn) for fn in pm.q_reward_fn]

    # Create a window
    win, background, aspect_ratio = get_win_obj(mouse_visible=False)

    # Initialization
    if exp_info['run'] == '01': # only present the instructions at the first run
        fl.type_text("Nous allons présenter les instructions.\nAppuyez sur la touche ESPACE pour continuer.",
            win,
            height=pm.text_height,
            background=background,
            t=pm.t
        )
        event.waitKeys(keyList=['space'])

    with open(pm.instr_fn, "r", encoding="utf-8") as file:
        instructions_text = file.read()

    instructions = visual.TextStim(
        win, text=instructions_text, font="Arial", color='black',  height=pm.text_height,
        alignText="center" 
    )

    background.draw()
    instructions.draw()
    win.flip()

    fl.check_escape(win, logger)
    event.waitKeys(keyList=['space'])
    logger.info('Instructions successfully presented.')

    # set a random seed for the sequence generation, to be able to reproduce the same sequences during questions
    if debugging:
        seed = pm.seed
    else:
        seed = random.randint(0, 1000)
    random.seed(seed)
    # Generate the multimodal sequences of items
    try:
        sm.check_nstims(pm.categories, pm.input_dir)
        sm.check_img_txt(pm.input_dir)
        amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, seed=seed)
        run_org = sm.distribute_sequences_block(sequences=amodal_sequences, n_blocks=pm.n_blocks)
        # define modality of questions in each trial
        question_mod_org = sm.distribute_mod_quest(n_blocks=pm.n_blocks, n_trials=pm.n_trials)
        first_seq_mod_org = sm.distribute_mod_seq(n_block=pm.n_blocks)
        logger.info('Sequences successfully generated.')
        logger.info('sequences: ' + str(amodal_sequences))
        logger.info('run organization: ' + str(run_org))
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, win)

    data = [] # data store for responses

    # utils = Utils(debugging=debugging,
    #     pport=pport,
    #     logger=logger,
    #     win=win, 
    #     aspect_ratio=aspect_ratio, 
    #     background=background, 
    #     wait_fun=core.wait,
    #     event_fun=event.waitKeys, 
    #     trig_fun=pport.signal
    # )

    utils = { # store some variables there because they will be used in several functions
        'debugging': debugging,
        'pport': pport,
        'logger': logger,
        'win': win,
        'aspect_ratio': aspect_ratio,
        'background': background,
        'wait_fun': core.wait,
        'event_fun': event.getKeys,
        'trig_fun': pport.signal,
        'clear_event_fun':event.clearEvents,
    }

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
                    units='norm'
                )
                
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
                    first_seq_mod = first_seq_mod_org[f'block{block_id}'][j]
                    start_with_img = True if first_seq_mod == 'img' else False
                    trial_mod_org = sm.generate_modalities(start_with_img=start_with_img) 

                    logger.info(f'trial: {trial_id}')
                    logger.info('block modalities order: ' + str(trial_mod_org))
                    logger.info('block sequences order: ' + str(trial_seq_org))

                    present_sequences(utils, amodal_sequences, trial_seq_org, trial_mod_org)
                                
                    # Ask questions. 3 questions, one for each amodal sequence. 
                    points_attributed = 0
                    question_modalities = question_mod_org[f'block{block_id}'][f'trial{trial_id}']
                    for m, seq_name in enumerate(trial_seq_org[0:3]):
                        
                        if ignore_q:
                            continue

                        question_id = m + 1 
        
                        logger.info(f'question number: {question_id}')
                        logger.info(f'sequence name: {seq_name}')
                        fl.check_escape(win, logger)

                        sequence = amodal_sequences[seq_name] # redefine the sequence to be used for the question
                        if seq_name in items_used_for_questions: # check if the items used for the question have already been used
                            ignore_idx = items_used_for_questions[seq_name]
                        else:
                            ignore_idx = None
                        idx1, idx2 = sm.draw_two(ignore_idx=ignore_idx) # draw two items from the sequence (e.g. (0, 4))

                        first_for_question = sequence[idx1] # first item to be presented for the question (e.g. 'cow')
                        second_for_question = sequence[idx2]
                        #first_in_seq = sequence[np.min([idx1, idx2])] # good answer as a string (e.g. 'cow')

                        if seq_name in items_used_for_questions: # store idx of items used for this sequence
                            items_used_for_questions[seq_name].extend([idx2])
                        else:
                            items_used_for_questions[seq_name] = [idx2]

                        # randomly select in which modality the question will be asked
                        modality = question_modalities[m]
                        stims = sm.get_stims(pm.input_dir, sequence, modality)
                        cat1 = sm.get_cat_from_stim(stims[idx1])
                        cat2 = sm.get_cat_from_stim(stims[idx2])
                        triggers = [pm.triggers[cat1][modality]['quest'],
                                    pm.triggers[cat2][modality]['quest']]
                        rt_clock = core.Clock()

                        logger.info(f'first item on screen: {first_for_question}')
                        logger.info(f"first item's index: {idx1}")
                        logger.info(f"first item's category: {cat1}")
                        logger.info(f'second item on screen: {second_for_question}')
                        logger.info(f"second item's index: {idx2}")
                        logger.info(f"second item's category: {cat2}")
                        
                        slot_positions = sm.get_slot_pos(y_pos=pm.y_pos)
                        slots = [
                            {
                                "rect": visual.Rect(
                                    win,
                                    width=pm.q_slot_size,
                                    height=pm.q_slot_size * aspect_ratio,
                                    pos=pos,
                                    lineColor="black",
                                    fillColor=(105, 105, 105)),
                                "highlight": visual.Rect(
                                    win,
                                    width=pm.hl_size,
                                    height=pm.hl_size * aspect_ratio,
                                    pos=pos,
                                    lineColor="blue",
                                    lineWidth=5,
                                    opacity=0,
                                ),
                                "selected": False,
                            }
                            for pos in slot_positions
                        ]

                        text_q_lst = ["Visualisez la sequence", "Placez l'item à la bonne position"]
                        instructions = [visual.TextStim(win=win,
                                text=txt,
                                pos=(0, 0.55),
                                height=pm.text_height,
                                color='black',
                                units='norm'
                            ) for txt in text_q_lst
                        ]

                        start_item= visual.ImageStim(
                            win,
                            image=stims[idx1],
                            pos=(-0.75, pm.y_pos),
                            size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
                        )

                        end_item = visual.ImageStim(
                            win,
                            image=stims[idx2],
                            pos=(0, -pm.y_pos),
                            size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
                        ) 
  
                        resp_idx, rt = sm.run_question(utils=utils,
                            slots=slots,
                            start_item=start_item,
                            end_item=end_item,
                            instructions=instructions,
                            triggers=triggers,
                            rt_clock=rt_clock,
                            global_clock=core.Clock()
                        )

                        distance = sm.get_response_distance(resp_idx, idx2, rt)
                        feedback_txt, font_color, correct, n_points = sm.get_feedback_args(distance)
                        points_attributed += n_points

                        fl.check_escape(win, logger)

                        feedback = visual.TextStim(win=win,
                            text=feedback_txt,
                            pos=(0, 0),
                            font="Arial",
                            color=font_color, 
                            height=pm.text_height,
                            units='norm',
                            bold=True
                        )
                        
                        # add sound selection and play
                        reward_sound = sm.get_reward_sound(q_reward_sounds, n_points)
                        
                        background.draw()
                        feedback.draw()
                        win.flip()
                        if reward_sound is not None:
                            reward_sound.play()
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
                            'correct_answer': idx2,
                            'response': resp_idx,
                            'distance': distance,
                            'correct': correct,
                            'rt': rt}
                        )

                        pd.DataFrame(data).to_csv(f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}.csv", index=False)
                        core.wait(0.5)
                    
                    # encouraging message
                    provide_trial_feedback(utils, points_attributed, reward_max, block_id, trial_id)

                logger.info(f'Block {block_id} completed successfully.')
                logger.info('========== End of block ==========')
            except Exception as exc:
                fl.log_exceptions(f"Error during run {exp_info['run']}, block {block_id}: {exc}", logger, win)

        logger.info(f'Run {exp_info["run"]} completed successfully.')
        logger.info('=============== End of run ===============')

        return exp_info, seed, win

    except Exception as exc:
        fl.log_exceptions(f"An error occurred during the run {exp_info['run']}: {exc}", logger, win)

def provide_trial_feedback(utils, points_attributed, reward_max, block_id, trial_id):

    if points_attributed > 6:
         reward_max.play() 
    trial_feedback = sm.get_trial_feedback(n_points=points_attributed, max_points=pm.max_points)

    if trial_id == 3:
        block_info = f"Fin du bloc {block_id}. Le bloc suivant va commencer."
    else:
        block_info = "L'essai suivant va commencer."

    fl.type_text(f"{trial_feedback} \n{block_info}",
        utils['win'],
        height=pm.text_height,
        background=utils['background'],
        t=pm.t
    )
    if utils['debugging']:
        core.wait(0.1)
    else:
        core.wait(3)

def present_sequences(utils, amodal_sequences, trial_seq_org, trial_mod_org):
    logger = utils['logger']
    for k, modality in enumerate(trial_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
        sequence_name = trial_seq_org[k]
        sequence = amodal_sequences[sequence_name]
        stims = sm.get_stims(pm.input_dir, sequence, modality)

        logger.info(f'sequence number: {k+1}')
        logger.info(f'sequence name: {sequence_name}')
        logger.info(f'sequence modality: {modality}')

        present_stimuli(utils, sequence, stims, modality)


def present_stimuli(utils, sequence, stims, modality):
    debugging = utils['debugging']
    for l, stim in enumerate(stims):  # noqa: E741
        if debugging:
            continue
        present_stimulus(utils, sequence, l, stim, modality)

def present_stimulus(utils, sequence, l, stim, modality):
    
    debugging = utils['debugging']
    pport = utils['pport']
    logger = utils['logger']
    win = utils['win']
    aspect_ratio = utils['aspect_ratio']
    background = utils['background']

    stim_cat = sm.get_cat_from_stim(stim)
    trig = pm.triggers[stim_cat][modality]['seq'] # keys are 'img'/'txt' and 'seq'/'quest'
                        
    fl.check_escape(win, logger)
    stim_image = visual.ImageStim(win=win,
        image=stim,
        size=(pm.img_size, pm.img_size*aspect_ratio)
    )
                                                    
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
        units='norm'
    )
    background.draw()
    fix_cross.draw()
    win.flip()
    if debugging:
        core.wait(0.5)
    else:
        core.wait(pm.isi_dur)

#############

def clear_stuff(win):
    win.flip()
    core.wait(0.5)
    event.clearEvents()

def run_and_question(run_id):
    exp_info, seed, win = run(debugging=True, ignore_q=True)
    clear_stuff(win)
    ask_all_seq(subject_id=exp_info['ID'], run_id=exp_info['run'], seed=seed, win=None)
    win.close()

if __name__ == '__main__':
    
    run_and_question(1)
    run_and_question(2)
    core.quit()