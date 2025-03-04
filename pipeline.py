import os
import logging
import glob
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event, sound
import pandas as pd
from sequences import stimuli_manager as sm
from sequences import flow as fl
from sequences import params as pm
from sequences import instr as it
import byte_triggers as bt
from sequences.common import get_win_dict
from bonus_question import ask_all_seq

def execute_run(debugging=False):
    ''' Main function, it executes a run of the experiment. Need to be called twice for the full experiment.

    Parameters
    ----------
    debugging : bool
        If True, the run will be executed in debugging mode, which means that the stimuli will be presented for a shorter duration.

    Returns
    -------
    tools : dict
        Dictionary containing the tools needed for the experiment (needed to transfer the window to the bonus questions).
    '''
    tools = initialize_run(debugging) # seed is set here. Tools contains a lot of useful stuff
    logger = tools['logger']
    exp_info = tools['exp_info']
    # Generate the multimodal sequences of items and the organization of the modality for presenation and questions
    try:
        amodal_sequences, question_mod_org, first_seq_mod_org = setup_sequence_distribution(tools)
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, tools['win'])
    two_run_org = sm.generate_run_org(amodal_sequences, seed=tools['seed']) # get the global oorganization of sequences for the two runs
    run_org = two_run_org[f'run{int(exp_info["run"])}'] # get the organization of sequences for the current run
    logger.info(f'=============== Start of run {exp_info["run"]} ===============')
    logger.info(f'run org: {run_org}')
    present_instructions(tools) # Present instructions 
    # define the tracker to keep track of where we are in the experiment
    tracker = { 
        'data': [], 
        'block_id': 0, 
        'trial_id': 0, 
        'question_id': 0, 
        'points_attributed': 0, 
        'used_items': {}
    }

    # iterate over the blocks - the actual experiment
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

        return tools
    
    except Exception as exc:
        fl.log_exceptions(f'An error occurred during the run {tools["exp_info"]["run"]}, block {tracker["block_id"]}: {exc}', 
            logger, 
            tools["win"])

def execute_block(tools, amodal_sequences, question_mod_org, first_seq_mod_org, tracker, block_org):
    ''' Executes a full block: sequence presentation and questioning. Returns the updated tracker.
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    amodal_sequences : dict
        Dictionary containing the multimodal sequences of items. {sequence_name: [item1, item2, ...]}
    question_mod_org : dict
        Dictionary containing the organization of the modalities for the questions. {block1: {trial1: [mod1, mod2, ...]}}
    first_seq_mod_org : dict
        Dictionary containing the organization of the modalities for the first sequence of each trial. {block1: [mod1, mod2, ...]}
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    block_org : dict
        Dictionary containing the organization of the sequences for each block. {trial1: [sequence1, sequence2, ...]}
        
    Returns
    -------
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    '''

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
    ''' Asks 3 questions and give feedbacks for a given trial. Returns the updated tracker.
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    amodal_sequences : dict
        Dictionary containing the multimodal sequences of items. {sequence_name: [item1, item2, ...]}
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    trial_seq_org : list
        List containing the sequences for the trial. e.g. ['A', 'B', 'C', 'A', 'B', 'C']
    question_mod_org : dict
        Dictionary containing the organization of the modalities for the questions. {block1: {trial1: [mod1, mod2, ...]}}

    Returns
    -------
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    '''
    
    tracker['points_attributed'] = 0 # reset points for each trial
    question_modalities = question_mod_org[f'block{tracker["block_id"]}'][f'trial{tracker["trial_id"]}']
    t_prep = pm.t_prep
    t_iqi = pm.t_iqi
    if tools['debugging']:
        t_prep = 0.01
        t_iqi = 0.01
    
    text = it.get_txt(tools['exp_info']['lang'], 'instr_q_fn')
    instructions = visual.TextStim(
        win=tools['win'],
        text=text,
        pos=(0, 0.55),
        height=pm.text_height,
        color='black',
        units='norm'
    ) 

    tools['background'].draw()
    instructions.draw()
    tools['win'].flip()
    core.wait(t_prep)

    for m, seq_name in enumerate(trial_seq_org[0:3]): # 3 questions per trial because 3 sequences presented twice
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
        subject_id = tools['exp_info']['ID']
        pd.DataFrame(tracker['data']).to_csv(f"{out_dir}/sub-{subject_id}_run-{run_id}.csv", index=False)
        core.wait(t_iqi)
                
    # encouraging message
    provide_trial_feedback(
        tools=tools, 
        tracker=tracker
    )

    return tracker

def initialize_run(debugging):
    ''' Initializes a run. Creates the output dir, set or get the seed to control randomization and 
    returns a dictionary containing the tools needed for the experiment (window, pport etc).'''

    exp_info = {
        'ID': '00',
        'run': '01',
        'lang': 'fr'
    }

    dlg = DlgFromDict(exp_info, title='Enter participant info', sortKeys=False)
    fl.handle_user_cancel(dlg)
    fl.check_user_info(exp_info)

    out_dir = f"data/output/sub-{exp_info['ID']}"
    logfn = f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}_cmseq-logs-{datetime.now().strftime('%Y%m%d-%H%M')}.log"
    os.makedirs(out_dir, exist_ok=True)

    if len(os.listdir(out_dir)) > 10: # check if the output directory is not filled with old files
        if not debugging:
            print(f"--- Output directory {out_dir} is not empty, exiting... ---")
            quit()
        else:
            files = glob.glob(f"{out_dir}/*")
            if exp_info['run'] == '01':
                if f'{out_dir}/seed.txt' in files:
                    files.remove(f'{out_dir}/seed.txt') # keep the seed file
                for f in files:
                    os.remove(f)

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

    if exp_info['run'] == '01': # if the experiment crashes, the sequences and run org will be the same
        seed = sm.w_and_set_seed(debugging, out_dir)
    else:
        seed = sm.r_and_set_seed(out_dir) 

    logger = logging.getLogger()
    logger.info('Experiment started.')
    logger.info(f'Seed: {seed}')
    logger.info(f'Participant ID: {exp_info["ID"]}')
    logger.info(f'Run number: {exp_info["run"]}')
    logger.info(f'Language: {exp_info["lang"]}')

    reward_max = sound.Sound(pm.sound0_fn)
    q_reward_sounds = [sound.Sound(fn) for fn in pm.q_reward_fn]
    win_dict = get_win_dict()
    win_dict['win'].mouseVisible = False

    tools = {
        'debugging': debugging,
        'pport': pport,
        'logger': logger,
        'win': win_dict['win'],
        'aspect_ratio': win_dict['aspect_ratio'],
        'background': win_dict['background'],
        'wait_fun': core.wait,
        'event_fun': event.getKeys,
        'trig_fun': pport.signal,
        'clear_event_fun':event.clearEvents,
        'exp_info': exp_info,
        'q_reward_sounds': q_reward_sounds,
        'reward_max': reward_max,
        'seed': seed,
        'out_dir': out_dir
    }
    
    return tools

def present_instructions(tools):
    '''Presents the instructions to the participant.'''

    exp_info = tools['exp_info']
    win = tools['win']
    background = tools['background']

    def present(instr):
        background.draw()
        instr.draw()
        win.flip()
        fl.check_escape(tools)
        event.waitKeys(keyList=['space'])

    if exp_info['lang'] == 'fr':
        txt = "Nous allons présenter les instructions.\nAppuyez sur la touche ESPACE pour continuer."
    else:
        txt = "We are going to present the instructions.\nPress the SPACE key to continue."
    if exp_info['run'] == '01': # only present the instructions at the first run
        fl.type_text(
            text=txt,
            win=win,
            height=pm.text_height,
            background=background,
            t=pm.t
        )
        event.waitKeys(keyList=['space'])

    instr1 = it.get_txt(exp_info['lang'], 'instr1_fn')
    instr2 = it.get_txt(exp_info['lang'], 'instr2_fn')

    instr_objects = [visual.TextStim(
        win,
        text=instr, 
        font="Arial", 
        color='black',  
        height=pm.text_height,
        alignText="center" 
        ) for instr in [instr1, instr2]
    ]

    for instr in instr_objects:
        present(instr)

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
    sm.check_nstims(pm.categories, pm.input_dir, tools['exp_info']['lang'])
    sm.check_img_txt(pm.input_dir, tools['exp_info']['lang'])
    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang=tools['exp_info']['lang'])
    # define modality of questions in each trial
    question_mod_org = sm.distribute_mod_quest(n_blocks=pm.n_blocks, n_trials=pm.n_trials)
    first_seq_mod_org = sm.distribute_mod_seq(n_block=pm.n_blocks)

    logger = tools['logger']
    logger.info('Sequences successfully generated.')
    logger.info('sequences: ' + str(amodal_sequences))

    return amodal_sequences, question_mod_org, first_seq_mod_org

def ask_trial_question(tools, tracker, amodal_sequences, question_modalities, seq_name):
    ''' Ask a question for a given sequence. Shows the two items and the slots for the response. 
    Put some info about the response in the tracker's 'data' slot to get a formated csv at the end for faster analysis.
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    amodal_sequences : dict
        Dictionary containing the multimodal sequences of items. {sequence_name: [item1, item2, ...]}
    question_modalities : dict
        Dictionary containing the organization of the modalities for the questions. {block1: {trial1: [mod1, mod2, ...]}}
    seq_name : str
        The name of the sequence to be used for the question.
        
    Returns
    -------
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    '''

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
    stims = sm.get_stims(pm.input_dir, sequence, modality, lang=exp_info['lang'])
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

    cue_viz = visual.ImageStim(
        win,
        image=stims[idx1],
        pos=(0, 0),
        size=(pm.img_size, pm.img_size * aspect_ratio),
    )
    cue_seq = visual.ImageStim(
        win,
        image=stims[idx1],
        pos=(-0.75, pm.y_pos),
        size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
    )
    target_viz = visual.ImageStim(
        win,
        image=stims[idx2],
        pos=(0, 0),
        size=(pm.img_size, pm.img_size * aspect_ratio),
    ) 
    target_seq = visual.ImageStim(
        win,
        image=stims[idx2],
        pos=(0, -pm.y_pos),
        size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
    ) 
    rt_clock = core.Clock()
    fade_clock = core.Clock()
    t_viz_cue = pm.t_viz_cue
    t_viz_target = pm.t_viz_target
    t_act = pm.t_act
    t_fb = pm.t_fb
    # if tools['debugging']:
    #     t_viz_cue = 0.1
    #     t_viz_target = 0.1
    #     t_act = 0.1
    #     t_fb = 0.1

    background.draw()
    cue_viz.draw()
    win.callOnFlip(tools['pport'].signal, triggers[0])
    win.flip()
    sm.fade_out(tools, cue_viz, clock=fade_clock, f_dur=t_viz_cue)

    background.draw()
    target_viz.draw()
    win.callOnFlip(tools['pport'].signal, triggers[1])
    win.flip()
    core.wait(t_viz_target)

    resp_idx, rt = sm.run_question(
        tools=tools,
        slots=slots,
        start_item=cue_seq,
        end_item=target_seq,
        rt_clock=rt_clock,
        global_clock=core.Clock(),
        t_act=t_act,
    )

    distance = sm.get_response_distance(resp_idx, idx2, rt)
    feedback_txt, font_color, correct, n_points = sm.get_feedback_args(distance, lang=exp_info['lang'])
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
    core.wait(t_fb)
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
    ''' Get the sequences and modalities for a given trial. Returns the ordered sequences and modalities (lists).
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    first_seq_mod_org : dict
        Dictionary containing the organization of the modalities for the first sequence of each trial. {block1: [mod1, mod2, ...]}
    block_org : dict
        Dictionary containing the organization of the sequences for the block with format: {trial1: ['A', 'B', 'C', 'A', 'B', 'C'], 'trial2': ['C', 'A', 'B'...}

    Returns
    -------
    trial_seq_org : list
        List containing the sequences for the trial. e.g. ['A', 'B', 'C', 'A', 'B', 'C']
    trial_mod_org : list
        List containing the modalities for the trial. e.g. ['img', 'txt', 'img', 'txt', 'img', 'txt']
    '''

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
    ''' Initialize a block. Returns the a dict with the organization of the sequences for the block with format:
    {'trial1': ['A', 'B', 'C', 'A', 'B', 'C'], 'trial2': ['C', 'A', 'B'...}
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    tracker : dict
        Dictionary containing the tracking variables for the experiment.
    run_org : dict
        Dictionary containing the organization of the sequences for each block. {block1:[sequence1, sequence2, ...]}'''

    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    chosen_sequences = run_org[f'block{tracker["block_id"]}']
    logger.info(f'block: {tracker["block_id"]}')
    logger.info(f'sequences: {chosen_sequences}')

    if tools['exp_info']['lang'] == 'fr':
        txt = f"Bloc {tracker['block_id']} \nAppuyez sur la touche ESPACE pour commencer!"
    else:
        txt = f"Block {tracker['block_id']} \nPress the SPACE key to start!"
    block_info = visual.TextStim(win=win,
        text=txt,
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
    ''' Provide feedback at the end of a trial. Returns nothing. '''

    t_post_q = pm.t_post_q
    if tools['debugging']:
        t_post_q = 0.01

    if tracker['points_attributed'] > 6:
        tools['reward_max'].play() 
    trial_feedback = sm.get_trial_feedback(
        n_points=tracker['points_attributed'], 
        max_points=pm.max_points, 
        lang=tools['exp_info']['lang']
    )

    if tracker['trial_id'] == 3:
        if tools['exp_info']['lang'] == 'fr':
            block_info = f"Fin du bloc {tracker['block_id']}. Le bloc suivant va commencer."
        else:
            block_info = f"End of block {tracker['block_id']}. The next block will start."
    else:
        if tools['exp_info']['lang'] == 'fr':
            block_info = "L'essai suivant va commencer."
        else:
            block_info = "The next trial will start."
       

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
    core.wait(t_post_q)
    return None

def present_sequences(tools, amodal_sequences, trial_seq_org, trial_mod_org):
    ''' Present the 6 sequences of a trial before the questions. Returns nothing. '''
    logger = tools['logger']
    for k, modality in enumerate(trial_mod_org): # loop over the 6 sequences (e.g. A, B, C * the two modalities (img, txt))
        sequence_name = trial_seq_org[k]
        sequence = amodal_sequences[sequence_name]
        stims = sm.get_stims(pm.input_dir, sequence, modality, lang=tools['exp_info']['lang'])
        logger.info(f'sequence number: {k+1}')
        logger.info(f'sequence name: {sequence_name}')
        logger.info(f'sequence modality: {modality}')
        present_stimuli(tools, sequence, stims, modality)

def present_stimuli(tools, sequence, stims, modality):
    ''' Present the 6 stimuli of a sequence. Returns nothing. '''
    debugging = tools['debugging']
    for i, stim in enumerate(stims):
        if debugging:
            continue
        present_stimulus(tools, sequence, i, stim, modality)
    return None

def present_stimulus(tools, sequence, i, stim, modality):
    ''' Present a single stimulus. Returns nothing. '''
    
    debugging = tools['debugging']
    pport = tools['pport']
    logger = tools['logger']
    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    t_stim = pm.stim_dur # where should the jitter be added? Stim or ISI?
    t_isi = pm.isi_dur + sm.jitter_isi(pm.jitter)
    if debugging:
        t_stim = 0.01
        t_isi = 0.01

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
    logger.info(f'stimulus number: {i+1}')
    logger.info(f'stimulus name: {str(sequence[i])}')
    logger.info(f'stimulus category: {stim_cat}')
    logger.info(f'stimulus path: {stim}')

    win.callOnFlip(pport.signal, trig)
    win.flip()
    core.wait(t_stim)

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
    core.wait(t_isi)
    return None

#########################
# highest level functions

def clear_stuff(win):
    win.flip()
    core.wait(0.5)
    event.clearEvents()

def pipeline(debugging=False):
    tools = execute_run(debugging=debugging)
    clear_stuff(tools['win'])
    ask_all_seq(
        subject_id=tools['exp_info']['ID'], 
        run_id=tools['exp_info']['run'], 
        lang=tools['exp_info']['lang'],
        win_dict=tools,
    )
    core.quit()

def test_pipeline(debugging=True):
    tools = execute_run(debugging)
    tools['win'].close()

if __name__ == '__main__':
    pipeline(debugging=True)