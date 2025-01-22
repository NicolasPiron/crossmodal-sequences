import os
import logging
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import pandas as pd
from utils import stimuli_manager as sm
from utils import flow as fl
from utils import params as pm
import byte_triggers as bt
from utils.common import get_win_obj
from bonus_question import ask_all_seq

def execute_run(run_org, debugging=False):
    ''' Function to execute a run of the experiment. Need to be called twice for the full experiment.

    Parameters
    ----------
    run_org : dict
        Dictionary containing the organization of the sequences for each block. {run1: {block1: [sequence1, sequence2, ...]}}
    debugging : bool
        If True, the run will be executed in debugging mode, which means that the stimuli will be presented for a shorter duration.

    Returns
    -------
    exp_info : dict
        Dictionary containing the participant's ID and the run number.
    win : psychopy.visual.Window
        The window object used for the experiment. It is fed to the bonus question module. 
    '''
    tools = initialize_experiment(debugging)
    logger = tools['logger']
    win = tools['win']
    exp_info = tools['exp_info']
    run_org = run_org[f'run{int(exp_info["run"])}']
    logger.info(f'=============== Start of run {exp_info["run"]} ===============')
    logger.info(f'run org: {exp_info["run"]}')
    present_instructions(tools) # Present instructions 
    # Generate the multimodal sequences of items
    try:
        amodal_sequences, question_mod_org, first_seq_mod_org = setup_sequence_distribution(tools)
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, tools['win'])

    tracker = {
        'data': [], 
        'block_id': 0, 
        'trial_id': 0, 
        'question_id': 0, 
        'points_attributed': 0, 
        'used_items': {}
    }

    try:

        for i in range(pm.n_blocks): # 4 blocks in a run
            tracker['block_id'] = i + 1
            block_org = initialize_block(
                tools=tools,
                tracker=tracker,
                run_org=run_org
            )
            tracker = execute_block(
                tools, 
                amodal_sequences, 
                question_mod_org, 
                first_seq_mod_org, 
                tracker, 
                block_org
            )
            
        logger.info(f'Run {tools["exp_info"]["run"]} completed successfully.')
        logger.info('=============== End of run ===============')

        return exp_info, win
    
    except Exception as exc:
        fl.log_exceptions(f'An error occurred during the run {tools["exp_info"]["run"]}, block {tracker["block_id"]}: {exc}', 
            logger, 
            tools["win"])

def execute_block(tools, amodal_sequences, question_mod_org, first_seq_mod_org, tracker, block_org):

    for j in range(pm.n_trials): # 3 trials for a block
        tracker['trial_id'] = j + 1
        trial_seq_org, trial_mod_org = initialize_trial_sequences(
                    tools=tools,
                    tracker=tracker,
                    first_seq_mod_org=first_seq_mod_org,
                    block_org=block_org
                )
        present_sequences(
                    tools=tools,
                    amodal_sequences=amodal_sequences, 
                    trial_seq_org=trial_seq_org, 
                    trial_mod_org=trial_mod_org
                )
                            
        tracker = handle_questioning(
                    tools=tools, 
                    amodal_sequences=amodal_sequences, 
                    tracker=tracker, 
                    trial_seq_org=trial_seq_org, 
                    question_mod_org=question_mod_org
                )
        
    logger = tools['logger']
    logger.info(f'Block {tracker["block_id"]} completed successfully.')
    logger.info('========== End of block ==========')

    return tracker

def handle_questioning(tools, amodal_sequences, tracker, trial_seq_org, question_mod_org):

    tracker['points_attributed'] = 0 # reset points for each trial
    question_modalities = question_mod_org[f'block{tracker["block_id"]}'][f'trial{tracker["trial_id"]}']
    
    for m, seq_name in enumerate(trial_seq_org[0:3]):
        tracker['question_id'] = m + 1
        tracker = ask_trial_question(
            tools=tools, 
            tracker=tracker,
            amodal_sequences=amodal_sequences,
            question_modalities=question_modalities,
            seq_name=seq_name
        )
        out_dir = tools['out_dir']
        run_id = tools['exp_info']['run']
        pd.DataFrame(tracker['data']).to_csv(f"{out_dir}/sub-{run_id}_run-{run_id}.csv", index=False)
        core.wait(0.5)
                
        # encouraging message
    provide_trial_feedback(
        tools=tools, 
        tracker=tracker
    )

    return tracker

def initialize_experiment(debugging):
    exp_info = {
        'ID': '00',
        'run': '01',
    }

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

    bt.add_file_handler(
        logfn,
        mode='a', 
        verbose='INFO'
    )
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
    win, background, aspect_ratio = get_win_obj(mouse_visible=False)

    tools = {
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
        'exp_info': exp_info,
        'q_reward_sounds': q_reward_sounds,
        'reward_max': reward_max,
        'out_dir': out_dir
    }
    
    return tools

def present_instructions(tools):
    ''' Function to present the instructions to the participant. '''
    exp_info = tools['exp_info']
    win = tools['win']
    background = tools['background']

    if exp_info['run'] == '01': # only present the instructions at the first run
        fl.type_text(
            "Nous allons présenter les instructions.\nAppuyez sur la touche ESPACE pour continuer.",
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
    fl.check_escape(tools)
    event.waitKeys(keyList=['space'])
    tools['logger'].info('Instructions successfully presented.')


def setup_sequence_distribution(tools):
    ''' Function to generate the sequences of items and the modality organization for the questions.

    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.

    Returns
    -------
    amodal_sequences : dict
        Dictionary containing the multimodal sequences of items. {sequence_name: [item1, item2, ...]}
    run_org : dict
        Dictionary containing the organization of the sequences for each block. {block1: [sequence1, sequence2, ...]}
    question_mod_org : dict
        Dictionary containing the organization of the modalities for the questions. {block1: {trial1: [mod1, mod2, ...]}}
    first_seq_mod_org : dict
        Dictionary containing the organization of the modalities for the first sequence of each trial. {block1: [mod1, mod2, ...]}
    '''
    sm.check_nstims(pm.categories, pm.input_dir)
    sm.check_img_txt(pm.input_dir)
    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
    # define modality of questions in each trial
    question_mod_org = sm.distribute_mod_quest(n_blocks=pm.n_blocks, n_trials=pm.n_trials)
    first_seq_mod_org = sm.distribute_mod_seq(n_block=pm.n_blocks)

    logger = tools['logger']
    logger.info('Sequences successfully generated.')
    logger.info('sequences: ' + str(amodal_sequences))

    return amodal_sequences, question_mod_org, first_seq_mod_org

def ask_trial_question(tools, tracker, amodal_sequences, question_modalities, seq_name):

    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    logger = tools['logger']
    exp_info = tools['exp_info']

    logger.info(f'question number: {tracker["question_id"]}')
    logger.info(f'sequence name: {seq_name}')
    fl.check_escape(tools)

    sequence = amodal_sequences[seq_name] # redefine the sequence to be used for the question
    if seq_name in tracker['used_items']: # check if the items used for the question have already been used
        ignore_idx = tracker['used_items'][seq_name]
    else:
        ignore_idx = None
    idx1, idx2 = sm.draw_two(ignore_idx=ignore_idx) # draw two items from the sequence (e.g. (0, 4))

    first_for_question = sequence[idx1] # first item to be presented for the question (e.g. 'cow')
    second_for_question = sequence[idx2]

    if seq_name in tracker['used_items']: # store idx of items used for this sequence
        tracker['used_items'][seq_name].extend([idx2])
    else:
        tracker['used_items'][seq_name] = [idx2]

    # randomly select in which modality the question will be asked
    modality = question_modalities[tracker['question_id'] - 1] # q_id - 1 = for m in questions
    stims = sm.get_stims(pm.input_dir, sequence, modality)
    cat1 = sm.get_cat_from_stim(stims[idx1])
    cat2 = sm.get_cat_from_stim(stims[idx2])
    triggers = [pm.triggers[cat1][modality]['quest'],
                pm.triggers[cat2][modality]['quest']]

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

    rt_clock = core.Clock()
    resp_idx, rt = sm.run_question(
        tools=tools,
        slots=slots,
        start_item=start_item,
        end_item=end_item,
        instructions=instructions,
        triggers=triggers,
        rt_clock=rt_clock,
        global_clock=core.Clock(),
        viz_t=pm.viz_t,
        act_t=pm.act_t
    )

    distance = sm.get_response_distance(resp_idx, idx2, rt)
    feedback_txt, font_color, correct, n_points = sm.get_feedback_args(distance)
    tracker['points_attributed'] += n_points

    fl.check_escape(tools)

    feedback = visual.TextStim(win=win,
        text=feedback_txt,
        pos=(0, 0),
        font="Arial",
        color=font_color, 
        height=pm.text_height,
        units='norm',
        bold=True
    )
    
    reward_sound = sm.get_reward_sound(tools['q_reward_sounds'], n_points)
                        
    background.draw()
    feedback.draw()
    win.flip()
    if reward_sound:
        reward_sound.play()
    core.wait(1)
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tracker['data'].append({
        'ID': exp_info['ID'],
        'run': exp_info['run'],
        'date': date,
        'block': tracker['block_id'],
        'trial': tracker['trial_id'],
        'question': tracker['question_id'],
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
    return tracker

def initialize_trial_sequences(tools, tracker, first_seq_mod_org, block_org):

    trial_seq_org = block_org[f'trial{tracker["trial_id"]}'] # e.g. ['A', 'B', 'C', 'A', 'B', 'C']
    first_seq_mod = first_seq_mod_org[f'block{tracker["block_id"]}'][tracker["trial_id"]-1]
    start_with_img = True if first_seq_mod == 'img' else False
    trial_mod_org = sm.generate_modalities(start_with_img=start_with_img) 

    logger = tools['logger']
    logger.info(f'trial: {tracker["trial_id"]}')
    logger.info('block modalities order: ' + str(trial_mod_org))
    logger.info('block sequences order: ' + str(trial_seq_org))

    return trial_seq_org,trial_mod_org

def initialize_block(tools, tracker, run_org):

    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    chosen_sequences = run_org[f'block{tracker["block_id"]}']
    logger.info(f'block: {tracker["block_id"]}')
    logger.info(f'sequences: {chosen_sequences}')

    block_info = visual.TextStim(win=win,
        text=f'Bloc {tracker["block_id"]} \nAppuyez sur la touche ESPACE pour commencer!',
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
    return block_org

def provide_trial_feedback(tools, tracker):

    if tracker['points_attributed'] > 6:
        tools['reward_max'].play() 
    trial_feedback = sm.get_trial_feedback(n_points=tracker['points_attributed'], max_points=pm.max_points)

    if tracker['trial_id'] == 3:
        block_info = f"Fin du bloc {tracker['block_id']}. Le bloc suivant va commencer."
    else:
        block_info = "L'essai suivant va commencer."
    txt =  f"{trial_feedback} \n{block_info}"

    text_stim = visual.TextStim(
        tools['win'], 
        text=txt, 
        font="Arial", 
        color='black', 
        height=pm.text_height,
        alignText="center"
    )    

    tools['background'].draw()
    text_stim.draw()
    tools['win'].flip()

    if tools['debugging']:
        core.wait(0.1)
    else:
        core.wait(3)

def present_sequences(tools, amodal_sequences, trial_seq_org, trial_mod_org):
    logger = tools['logger']
    for k, modality in enumerate(trial_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
        sequence_name = trial_seq_org[k]
        sequence = amodal_sequences[sequence_name]
        stims = sm.get_stims(pm.input_dir, sequence, modality)
        logger.info(f'sequence number: {k+1}')
        logger.info(f'sequence name: {sequence_name}')
        logger.info(f'sequence modality: {modality}')
        present_stimuli(tools, sequence, stims, modality)

def present_stimuli(tools, sequence, stims, modality):
    debugging = tools['debugging']
    for l, stim in enumerate(stims):  # noqa: E741
        if debugging:
            continue
        present_stimulus(tools, sequence, l, stim, modality)

def present_stimulus(tools, sequence, l, stim, modality): # noqa: E741
    
    debugging = tools['debugging']
    pport = tools['pport']
    logger = tools['logger']
    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']

    stim_cat = sm.get_cat_from_stim(stim)
    trig = pm.triggers[stim_cat][modality]['seq'] # keys are 'img'/'txt' and 'seq'/'quest'
                        
    fl.check_escape(tools)
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
    win.flip(clear_buffer=True)
    del stim_image
    
    if debugging:
        core.wait(0.5)
    else:
        core.wait(pm.isi_dur)

#########################
# highest level functions

def clear_stuff(win):
    win.flip()
    core.wait(0.5)
    event.clearEvents()

def run_and_question(run_org, debugging=False):
    exp_info, win = execute_run(run_org=run_org, debugging=debugging)
    clear_stuff(win)
    ask_all_seq(subject_id=exp_info['ID'], run_id=exp_info['run'], win=None)
    win.close()

def pipeline(debugging=False):
    if not debugging:
        sm.set_seed()
    else:
        sm.set_seed(seed=pm.seed)
    run_org = sm.generate_run_org(pm.input_dir, pm.seq_structures)
    run_and_question(run_org, debugging)
    run_and_question(run_org, debugging)
    core.quit()

if __name__ == '__main__':
    
    pipeline(debugging=False)