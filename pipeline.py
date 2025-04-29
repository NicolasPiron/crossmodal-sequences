import os
import sys
import shutil
import logging
import glob
import time
import random
import math
import pandas as pd
import numpy as np
import byte_triggers as bt
import platform
from datetime import datetime
from psychopy.gui import DlgFromDict
from psychopy.hardware.keyboard import Keyboard
from psychopy import visual, core, event, sound
from sequences import stimuli_manager as sm
from sequences import flow as fl
from sequences import params as pm
from sequences import instr as it
from sequences.common import get_win_dict
from bonus_question import bonus_question

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
    tools = initialize_run(debugging) # seed is set here. Tools contains a lot of useful stuff, including the tracker.
    logger = tools['logger']
    exp_info = tools['exp_info']
    # Generate the multimodal sequences of items and the organization of the modality for presenation and questions
    try:
        amodal_sequences, question_mod_org, first_seq_mod_org = setup_sequence_distribution(tools)
    except Exception as exc:
        fl.log_exceptions(f"An error occurred during sequence generation: {exc}", logger, tools['win'])

    sound_org = sm.distribute_snd(seq_names=list(amodal_sequences.keys()), snd_dir=pm.snd_stim_dir, seed=tools['seed']) # get the sound organization for the sequences
    tools['sound_org'] = sound_org 
    two_run_org = sm.generate_run_org(amodal_sequences, seed=tools['seed']) # get the global oorganization of sequences for the two runs
    run_org = two_run_org[f'run{int(exp_info["run"])}'] # get the organization of sequences for the current run

    full_block_org = {} # get the order of sequences for each block
    for block_id in run_org.keys():
        full_block_org[block_id] = sm.distribute_sequences_trial(sequence_names=run_org[block_id], n_trials=pm.n_trials)

    # get the rewarded sequences
    n_seq_rd = int(pm.n_seq / 2)
    all_reward_info = sm.get_reward_info(two_run_org, seed=tools['seed'], n=n_seq_rd)
    reward_info = all_reward_info[f'run{int(exp_info["run"])}']
    tools['reward_info'] = reward_info

    logger.info(f'=============== Start of run {exp_info["run"]} ===============')
    logger.info(f'expe org: {two_run_org}')
    logger.info(f'run org: {run_org}')
    logger.info(f'full block org: {full_block_org}')
    logger.info(f'all reward info: {all_reward_info}')
    logger.info(f'run reward info: {reward_info}')
    logger.info(f'question mod org: {question_mod_org}')
    logger.info(f'first seq mod org: {first_seq_mod_org}')
    logger.info(f'sound organization: {sound_org}')
    present_instructions(tools) # Present instructions 

    # if the user entered a block id != 1, we skip the first blocks
    if tools['starting_point'] is not None:
        n_skip = int(tools['starting_point']['block']) - 1 # -1 because we use indices but the user enters the block number
    else:
        n_skip = 0

    # iterate over the blocks - the actual experiment
    try:

        for i in range(n_skip+1, pm.n_blocks+1): # +1 because we want to include the last block and start from 1
            block_org = full_block_org[f'block{i}']
            tools['tracker']['block_id'] = i
            initialize_block(
                tools=tools,
                run_org=run_org
            )
            tools = execute_block(
                tools, 
                amodal_sequences, 
                question_mod_org, 
                first_seq_mod_org, 
                block_org
            )
            
        logger.info(f'Run {tools["exp_info"]["run"]} completed successfully.')
        logger.info('=============== End of core part ===============')

        return tools
    
    except Exception as exc:
        fl.log_exceptions(f'An error occurred during the run {tools["exp_info"]["run"]}, block {tools["tracker"]["block_id"]}: {exc}', 
            logger, 
            tools["win"])
        
def initialize_run(debugging):
    ''' Initializes a run. Creates the output dir, set or get the seed to control randomization and 
    returns a dictionary containing the tools needed for the experiment (window, pport etc).
    '''

    exp_info = {
        'ID': '00',
        'run': '01',
        'block': '04',
        'trial': '03',
        'seq': '06',
        'lang': 'fr'
    }

    dlg = DlgFromDict(exp_info, title='Enter participant info', sortKeys=False)
    fl.handle_user_cancel(dlg)
    fl.check_user_info(exp_info)

    # check if the user wants to start from a specific point
    keys_to_check = ['block', 'trial', 'seq']
    if any(int(exp_info[k]) > 1 for k in keys_to_check):
        starting_point = {k: int(exp_info[k]) for k in keys_to_check} # also convert to int
    else:
        starting_point = None

    out_dir = f"data/output/sub-{exp_info['ID']}"
    logfn = f"{out_dir}/sub-{exp_info['ID']}_run-{exp_info['run']}_cmseq-logs-{datetime.now().strftime('%Y%m%d-%H%M')}.log"
    os.makedirs(out_dir, exist_ok=True)

    fn_n_dir = os.listdir(out_dir)
    if len(fn_n_dir) > 10: # check if the output directory is not filled with old files
        if not debugging:
            #print('output dir not empty, overwriting')
            print(f"--- Output directory {out_dir} is not empty, exiting... ---")
            sys.exit()
        else:
            for f in fn_n_dir:
                full_path = os.path.join(out_dir, f)
                if os.path.isfile(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path) 

    # had to add this because the waitKeys function was not working with the version of Ubuntu on the stim PC
    if platform.system() == 'Linux':
        keyboard = Keyboard()
        keyboard.start()
        adapt_waitKeys = keyboard.waitKeys
    else:
        keyboard = None
        adapt_waitKeys = event.waitKeys

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
        pport = bt.ParallelPortTrigger(pm.pport, port_type='pport', delay=10)

    seed = sm.set_seed(exp_info['ID'])

    logger = logging.getLogger()
    logger.info(f'running on {platform.system()}')
    logger.info('Experiment started.')
    logger.info(f'Seed: {seed}')
    logger.info(f'Participant ID: {exp_info["ID"]}')
    logger.info(f'Run number: {exp_info["run"]}')
    logger.info(f'Language: {exp_info["lang"]}')

    reward_max = sound.Sound(pm.sound0_fn)
    q_reward_sounds = [sound.Sound(fn) for fn in pm.q_reward_fn]
    win_dict = get_win_dict()
    win_dict['win'].mouseVisible = False

    # define the tracker to keep track of where we are in the experiment
    tracker = { 
        'data': [], 
        'block_id': 0, 
        'trial_id': 0, 
        'question_id': 0, 
        'points_attributed': 0, 
        'used_items': {}
    }

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
        'out_dir': out_dir,
        'starting_point': starting_point,
        'tracker': tracker,
        'keyboard': keyboard,
        'adapt_waitKeys': adapt_waitKeys,
    }
    
    return tools

def execute_block(tools, amodal_sequences, question_mod_org, first_seq_mod_org, block_org):
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
    block_org : dict
        Dictionary containing the organization of the sequences for each block. {trial1: [sequence1, sequence2, ...]}
        
    Returns
    -------
    tools : dict
        Dictionary containing the tools needed for the experiment. The tracker is updated in this function.
    '''

    # this code has been added to handle the case where the user wants to start from a specific point
    # check if we are starting from a specific point (unusual case)
    if tools['starting_point'] is not None:
        if tools['starting_point']['block'] == tools['tracker']['block_id']: # if we are not in the specific starting block, start at 1 because
            # we are starting from the beginning of the block, as usual. 
            n_skip = int(tools['starting_point']['trial']) - 1
        else:
            n_skip = 0
    else:
        n_skip = 0

    for j in range(n_skip+1, pm.n_trials+1): # +1 because we want to include the last trial and start from 1.
        tools['tracker']['trial_id'] = j
        seq_sounds = {seq_n:sound.Sound(path) for seq_n, path in tools['sound_org'].items()} # sounds are loaded here
        #seq_sounds = None
        trial_seq_org, trial_mod_org = initialize_trial_sequences(
            tools=tools,
            first_seq_mod_org=first_seq_mod_org,
            block_org=block_org
        )
        present_sequences(
            tools=tools,
            amodal_sequences=amodal_sequences, 
            trial_seq_org=trial_seq_org, 
            trial_mod_org=trial_mod_org,
            seq_sounds=seq_sounds,
        )
                            
        tools = handle_questioning(
            tools=tools, 
            amodal_sequences=amodal_sequences, 
            trial_seq_org=trial_seq_org, 
            question_mod_org=question_mod_org
        )
    
    end_block_break_quest(tools)
    
    logger = tools['logger']
    logger.info(f'Block {tools["tracker"]["block_id"]} completed successfully.')
    logger.info('========== End of block ==========')

    return tools

def initialize_block(tools, run_org):
    ''' Initialize a block and log info. Returns nothing.
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.

    run_org : dict
        Dictionary containing the organization of the sequences for each block. {block1:[sequence1, sequence2, ...]}'''

    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    adapt_waitKeys = tools['adapt_waitKeys']
    tracker = tools['tracker'] # the tracker is extracted here but not modified (so no need to return it)
    chosen_sequences = run_org[f'block{tracker["block_id"]}']
    logger.info(f'block: {tracker["block_id"]}')
    logger.info(f'sequences: {chosen_sequences}')

    if tools['exp_info']['lang'] == 'fr':
        txt = f"Bloc {tracker['block_id']} \nAttendez le feu vert de l'experimentateur, puis appuyez sur le bouton central pour commencer!"
    else:
        txt = f"Block {tracker['block_id']} \nWait for the experimenter's signal, then press the middle key to start!"
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
    adapt_waitKeys(keyList=[pm.key_dict['confirm']])
    return

def end_block_break_quest(tools):
    ''' Presents the small Likert scale questions at the end of the block + a break.'''
    
    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    block_id = tools['tracker']['block_id']
    adapt_waitKeys = tools['adapt_waitKeys']

    # small waitkeys so the participant doesn't click automatically for the questionnaire
    instr_txt = it.get_txt(tools['exp_info']['lang'], 'quest_ready_fn')
    instr = visual.TextStim(win=win,
        text=instr_txt,
        pos=(0, 0),
        font="Arial",
        color='black', 
        height=pm.text_height,
        units='norm'
    )
    background.draw()
    instr.draw()
    win.flip()
    adapt_waitKeys(keyList=[pm.key_dict['confirm']])

    # ask how vigilant and focused questions
    vigi_text = it.get_txt(tools['exp_info']['lang'], 'quest_vigi_fn')
    st1, st2 = pm.stxt_dict[tools['exp_info']['lang']]['vigi'] 
    logger.info('Asking the vigilance question')
    vigi_resp = present_questionnaire(
        tools=tools, 
        text=vigi_text, 
        scale_text1=st1, 
        scale_text2=st2
    )
    logger.info(f"Block {block_id} vigilance response: {vigi_resp}")
    fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])

    focus_text = it.get_txt(tools['exp_info']['lang'], 'quest_focus_fn')
    st1, st2 = pm.stxt_dict[tools['exp_info']['lang']]['focus'] 
    logger.info('Asking the focus question')
    focus_resp = present_questionnaire(
        tools=tools, 
        text=focus_text,
        scale_text1=st1, 
        scale_text2=st2
    )
    logger.info(f"Block {block_id} focus response: {focus_resp}")
    fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])

    if tools['tracker']['block_id'] < 4: # break for the first 3 blocks, then another longer break is proposed
        post_block_break(tools)
        # ask what was the participant thinking about during break
        think_text = it.get_txt(tools['exp_info']['lang'], 'quest_think_fn')
        st1, st2 = pm.stxt_dict[tools['exp_info']['lang']]['think'] 
        logger.info('Asking the think question')
        think_resp = present_questionnaire(
            tools=tools, 
            text=think_text,
            scale_text1=st1, 
            scale_text2=st2 
        )
        logger.info(f"Block {block_id} thinking response: {think_resp}")
        fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])


def present_questionnaire(tools, text, scale_text1, scale_text2):
    ''' Function to present a questionnaire to the participant. It is a slider with 7 ticks.'''

    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    slider_pos = np.linspace(pm.far_l, pm.far_r, pm.n_ticks)
    start_pos = int(np.floor(pm.n_ticks / 2)) # start in the middle

    txt = visual.TextStim(
        win,
        text=text,
        height=pm.text_height,
        pos=(0, 0.5),
        color="black",
    )

    s1 = visual.TextStim(
        win,
        text=scale_text1,
        height=pm.text_height,
        pos=(pm.far_l, pm.y_bar+pm.stxt_up),
        color="black",
    )

    s2 = visual.TextStim(
        win,
        text=scale_text2,
        height=pm.text_height,
        pos=(pm.far_r, pm.y_bar+pm.stxt_up),
        color="black",
    )

    bar = visual.Rect(
        win,
        width=pm.bar_len,
        height=0.05*aspect_ratio,
        fillColor=pm.bar_c,
        pos=(0, pm.y_bar),
    )
    slider = visual.Rect(
        win,
        width=0.02,
        height=0.1*aspect_ratio,
        fillColor=pm.slider_c,
        lineColor=pm.slider_lc,
        pos=(slider_pos[start_pos], pm.y_bar),
    )

    ticks = [
        visual.Rect(
            win,
            width=0.01,
            height=0.05*aspect_ratio,
            fillColor=pm.tick_c,
            pos=(x, pm.y_bar),
        )
        for x in slider_pos
    ]

    def draw_all():
        background.draw()
        txt.draw()
        s1.draw()
        s2.draw()
        bar.draw()
        for tick in ticks:
            tick.draw()
        slider.draw()

    draw_all()
    win.flip()

    current_pos = start_pos
    run = True
    while run:
        keys = event.getKeys()
        if pm.key_dict['confirm'] in keys:
            run = False
        current_pos = sm.move_slider(slider, slider_pos, pm.y_bar, current_pos, keys, pm.key_dict)
        draw_all()
        win.flip()
        core.wait(0.001)

    slider.fillColor = pm.validation_c
    draw_all()
    win.flip()
    core.wait(0.5)
    background.draw()
    win.flip()
    core.wait(1.5)

    return current_pos+1

def post_block_break(tools):
    ''' Function to present a break between blocks. Returns nothing. '''
    win = tools['win']
    background = tools['background']
    aspect_ratio = tools['aspect_ratio']
    logger = tools['logger']
    pport = tools['pport']
    block_id = tools['tracker']['block_id']

    text = it.get_txt(tools['exp_info']['lang'], 'instr_pause_fn')
    instr = visual.TextStim(
        win=tools['win'],
        text=text,
        pos=(0, 0.5),
        height=pm.text_height,
        color='black',
        units='norm'
    ) 

    # load spinning wheel images 
    w_fns = sorted(glob.glob(f'{pm.spin_wheel_dir}/w*.png'))
    w_imgs = [
        visual.ImageStim(win, image=w_fn, size=(0.2, 0.2*aspect_ratio), units="norm")
        for w_fn in w_fns
    ]
    wclock = core.Clock()
    rclock = core.Clock()
    # log and triggers before and after break
    logger.info(f'block {block_id} break start')
    background.draw()
    instr.draw()
    win.callOnFlip(pport.signal, pm.triggers['misc']['block_pause'])
    win.flip()

    sm.display_wheel(tools, wclock, rclock, pm.t_post_block, pm.t_rotate, w_imgs, instr)

    pport.signal(pm.triggers['misc']['block_endpause'])
    logger.info(f'block {block_id} break stop')
    return

def post_run_break(tools, pause_i):
    ''' Break post run. Returns nothing. '''

    pport = tools['pport']
    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    aspect_ratio = tools['aspect_ratio']

    # for the questionnaire about thinking about sequences
    think_text = it.get_txt(tools['exp_info']['lang'], 'quest_think_fn')
    st1, st2 = pm.stxt_dict[tools['exp_info']['lang']]['think'] 

    # sound indicating the end of the break
    end_sound = sound.Sound(pm.snd_endPause_fn)
    # intructions
    text = it.get_txt(tools['exp_info']['lang'], 'instr_pause_fn')
    instr = visual.TextStim(
        win=tools['win'],
        text=text,
        pos=(0, 0.55),
        height=pm.text_height,
        color='black',
        units='norm'
    ) 
    # load spinning wheel images 
    w_fns = sorted(glob.glob(f'{pm.spin_wheel_dir}/w*.png'))
    w_imgs = [
        visual.ImageStim(win, image=w_fn, size=(0.2, 0.2*aspect_ratio), units="norm")
        for w_fn in w_fns
    ]
    wclock = core.Clock()
    rclock = core.Clock()
    # log and triggers before and after break
    logger.info(f'post run break {pause_i} start')
    background.draw()
    instr.draw()
    win.callOnFlip(pport.signal, pm.triggers['misc']['run_pause'])
    win.flip()

    sm.display_wheel(tools, wclock, rclock, pm.t_post_run, pm.t_rotate, w_imgs, instr)

    background.draw()
    instr.draw()
    #win.callOnFlip(end_sound.play)
    win.flip()
    core.wait(1) # wait for the sound to finish
    pport.signal(pm.triggers['misc']['run_endpause'])
    logger.info(f'post run break {pause_i} end')
    logger.info('Asking the think question')
    think_resp = present_questionnaire(
        tools=tools, 
        text=think_text,
        scale_text1=st1, 
        scale_text2=st2 
    )
    logger.info(f"Post run pause {pause_i} thinking response: {think_resp}")
    return

def play_tmr(tools):
    ''' Play the targeted memory reactivation sounds. Returns nothing. '''
    pport = tools['pport']
    logger = tools['logger']
    win = tools['win']
    background = tools['background']
    adapt_waitKeys = tools['adapt_waitKeys']

    # load instruction part
    text = it.get_txt(tools['exp_info']['lang'], 'instr_tmr1')
    instr1 = visual.TextStim(
        win=tools['win'],
        text=text,
        pos=(0, 0),
        height=pm.text_height,
        color='black',
        units='norm'
    ) 
    # load tmr part
    s_dict = {seq_n:sound.Sound(fn) for seq_n, fn in tools['sound_org'].items()}
    text = it.get_txt(tools['exp_info']['lang'], 'instr_tmr2')
    instr2 = visual.TextStim(
        win=tools['win'],
        text=text,
        pos=(0, 0),
        height=pm.text_height,
        color='black',
        units='norm'
    ) 

    # flow
    background.draw()
    instr1.draw()
    win.flip()
    adapt_waitKeys(keyList=[pm.key_dict['confirm']])

    background.draw()
    instr2.draw()
    win.flip()
    logger.info('Starting TMR')
    core.wait(pm.t_tmr_delay)

    for seq_n, snd in s_dict.items():
        logger.info(f"playing {tools['sound_org'][seq_n]} for sequence {seq_n}")
        jitter = random.choice([-pm.tmr_jitter, 0, pm.tmr_jitter])
        win.callOnFlip(pport.signal, pm.triggers['misc'][f'tmr_{seq_n}'])        
        win.callOnFlip(snd.play)
        background.draw()
        instr2.draw()
        win.flip()
        core.wait(pm.t_tmr_delay+jitter)

    logger.info('TMR successfully done')
    return

def handle_questioning(tools, amodal_sequences, trial_seq_org, question_mod_org):
    ''' Asks 3 questions and give feedbacks for a given trial. Returns the updated tracker.
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
    amodal_sequences : dict
        Dictionary containing the multimodal sequences of items. {sequence_name: [item1, item2, ...]}
    trial_seq_org : list
        List containing the sequences for the trial. e.g. ['A', 'B', 'C', 'A', 'B', 'C']
    question_mod_org : dict
        Dictionary containing the organization of the modalities for the questions. {block1: {trial1: [mod1, mod2, ...]}}

    Returns
    -------
    tools : dict
        Dictionary containing the tools needed for the experiment. The tracker is updated in this function.
    '''
    tracker = tools['tracker'] # I extract it here, and it is reasigned in tools at the end of the function
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
    tools['tracker'] = tracker
    return tools

def present_instructions(tools):
    '''Presents the instructions to the participant.'''

    exp_info = tools['exp_info']
    win = tools['win']
    background = tools['background']
    adapt_waitKeys = tools['adapt_waitKeys']

    def present(instr):
        background.draw()
        instr.draw()
        win.flip()
        fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])
        adapt_waitKeys(keyList=[pm.key_dict['confirm']])

    if exp_info['lang'] == 'fr':
        txt = "Nous allons présenter les instructions.\nAppuyez sur le bouton central pour continuer."
    else:
        txt = "We are going to present the instructions.\nPress the middle key to continue."
    if exp_info['run'] == '01': # only present the instructions at the first run
        fl.type_text(
            text=txt,
            win=win,
            height=pm.text_height,
            background=background,
            t=pm.t
        )
        adapt_waitKeys(keyList=[pm.key_dict['confirm']])

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
    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang=tools['exp_info']['lang'], seed=tools['seed'])
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

    #TODO: check tracker

    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    logger = tools['logger']
    exp_info = tools['exp_info']
    pport = tools['pport']

    logger.info(f'question number: {tracker["question_id"]}')
    logger.info(f'sequence name: {seq_name}')
    fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])

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

    triggers1 = [
        pm.triggers['seq_pos'][seq_name][idx1],
        pm.triggers['seq_pos'][seq_name][idx2]
    ]
    triggers2 = [
        pm.triggers['mod_cat'][modality][cat1],
        pm.triggers['mod_cat'][modality][cat2]
    ]

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

    # rectangle for photodiode
    rect = visual.Rect(
        win=win,
        width=0.05,
        height=0.05*aspect_ratio,
        pos=(1, 1),
        units='norm',
        fillColor=(255, 255, 255),
    )

    rt_clock = core.Clock()
    fade_clock = core.Clock()
    t_viz_cue = pm.t_viz_cue
    t_viz_target = pm.t_viz_target
    t_act = pm.t_act
    t_fb = pm.t_fb
    if tools['debugging']:
        t_viz_cue = 0.01
        t_viz_target = 0.01
        t_act = 0.01
        t_fb = 0.01

    background.draw()
    cue_viz.draw()
    rect.draw()
    win.callOnFlip(fl.novov_trigger,pport=pport, trig1=triggers1[0], trig2=triggers2[0], delay=10)
    win.flip()
    sm.fade_out(tools, cue_viz, clock=fade_clock, f_dur=t_viz_cue)

    background.draw()
    target_viz.draw()
    rect.draw()
    win.callOnFlip(fl.novov_trigger,pport=pport, trig1=triggers1[1], trig2=triggers2[1], delay=10)
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
        key_dict=pm.key_dict,
        trig_dict=pm.triggers
    )

    distance = sm.get_response_distance(resp_idx, idx2, rt)
    feedback_txt, font_color, correct, n_points = sm.get_feedback_args(distance, lang=exp_info['lang'])
    tracker['points_attributed'] += n_points
    fb_trig = 'fb_correct' if correct else 'fb_incorrect'

    fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])

    feedback = visual.TextStim(win=win,
        text=feedback_txt,
        pos=(0, 0),
        font="Arial",
        color=font_color, 
        height=pm.text_height,
        units='norm',
        bold=True
    )
     
    reward_sound = sm.get_fb_sound(tools['q_reward_sounds'], n_points)
                        
    background.draw()
    feedback.draw()
    win.callOnFlip(tools['pport'].signal, pm.triggers['misc'][fb_trig])
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

def initialize_trial_sequences(tools, first_seq_mod_org, block_org):
    ''' Get the sequences and modalities for a given trial. Returns the ordered sequences and modalities (lists).
    
    Parameters
    ----------
    tools : dict
        Dictionary containing the tools needed for the experiment.
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

    trial_seq_org = block_org[f'trial{tools["tracker"]["trial_id"]}'] # e.g. ['A', 'B', 'C', 'A', 'B', 'C']
    block_id = tools['tracker']['block_id'] # extract the block id for readability
    trial_id = tools['tracker']['trial_id']
    first_seq_mod = first_seq_mod_org[f'block{block_id}'][trial_id-1] # -1 because working with indices but the tracker starts at 1
    start_with_img = True if first_seq_mod == 'img' else False
    trial_mod_org = sm.generate_modalities(start_with_img=start_with_img) 

    logger = tools['logger']
    logger.info(f'trial: {tools["tracker"]["trial_id"]}')
    logger.info('trial modalities order: ' + str(trial_mod_org))
    logger.info('trial sequences order: ' + str(trial_seq_org))

    return trial_seq_org,trial_mod_org


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
            block_info = f"Fin du bloc {tracker['block_id']}. \nRépondez aux questions suivantes et profitez d'une courte pause."
        else:
            block_info = f"End of block {tracker['block_id']}. \nAnswer the following questions and enjoy a short break."
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
    return

def present_sequences(tools, amodal_sequences, trial_seq_org, trial_mod_org, seq_sounds):
    ''' Present the 6 sequences of a trial before the questions. Returns nothing. 
    Adapted so it can skip n sequences if the user wants to start from a specific sequence.'''
    logger = tools['logger']
    
    # check if we are starting from a specific point. If so, we skip the first sequences
    if tools['starting_point'] is not None:
        if (tools['starting_point']['trial'] == tools['tracker']['trial_id']) and (tools['starting_point']['block'] == tools['tracker']['block_id']):
            n_skip = int(tools['starting_point']['seq']) - 1
        else:
            n_skip = 0
    else:
        n_skip = 0

    for k in range(n_skip+1, pm.n_seq+1): # using +1 to be consistant with the other loops, but not the nicest way to do it (k-1 under)
        modality = trial_mod_org[k-1]
        sequence_name = trial_seq_org[k-1]
        sequence = amodal_sequences[sequence_name]
        snd_path = tools['sound_org'][sequence_name] # for the logger only
        snd = seq_sounds[sequence_name]
        #snd = None
        stims = sm.get_stims(pm.input_dir, sequence, modality, lang=tools['exp_info']['lang'])
        logger.info(f'sequence number: {k}')
        logger.info(f'sequence name: {sequence_name}')
        logger.info(f'sequence modality: {modality}')
        logger.info(f'sound name: {snd_path}')
        present_stimuli(tools, sequence, sequence_name, stims, modality, snd)
    return

def present_stimuli(tools, sequence, sequence_name, stims, modality, snd):
    ''' Present the 6 stimuli of a sequence. Returns nothing. '''
    debugging = tools['debugging']
    jitters = np.linspace(-pm.jitter, pm.jitter, pm.n_seq)
    random.shuffle(jitters)
    for i, stim in enumerate(stims):
        if debugging:
            continue
        present_stimulus(tools, sequence, sequence_name, i, stim, modality, jitters[i], snd)
    return

def present_stimulus(tools, sequence, sequence_name, i, stim, modality, jitter, snd): 
    ''' Present a single stimulus. Returns nothing. '''
    
    debugging = tools['debugging']
    pport = tools['pport']
    logger = tools['logger']
    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']

    t_stim = pm.stim_dur 
    t_isi = pm.isi_dur + jitter
    if debugging:
        t_stim = 0.01
        t_isi = 0.01

    stim_cat = sm.get_cat_from_stim(stim)
    trig1 = pm.triggers['seq_pos'][sequence_name][i] # key is seq name (e.g., 'A') and then index of the item to find trigger in the list
    trig2 = pm.triggers['mod_cat'][modality][stim_cat] # keys are 'img'/'txt' and category names (e.g., 'animals')
                        
    fl.check_escape_or_break(tools, pause_key=pm.key_dict['pause'])
    stim_image = visual.ImageStim(win=win,
        image=stim,
        size=(pm.img_size, pm.img_size*aspect_ratio)
    )

    # act a rectangle for photodiode
    rect = visual.Rect(
        win=win,
        width=0.05,
        height=0.05*aspect_ratio,
        pos=(1, 1),
        units='norm',
        fillColor=(255, 255, 255),
    )
    
    # Display fixation cross
    fix_cross = visual.TextStim(win=win,
        text='+',
        font='Arial',
        height=0.1,
        color='black',
        units='norm'
    )

    background.draw()
    rect.draw()
    stim_image.draw()
    # log info there to be closer to the actual presentation
    logger.info(f'stimulus number: {i+1}')
    logger.info(f'stimulus name: {str(sequence[i])}')
    logger.info(f'stimulus category: {stim_cat}')
    logger.info(f'stimulus path: {stim}')

    win.callOnFlip(fl.novov_trigger,pport=pport, trig1=trig1, trig2=trig2, delay=10)
    win.callOnFlip(snd.play) # play sound at the beginning of the stimulus presentation
    win.flip()
    t1 = time.time()
    core.wait(t_stim)
    #fl.wait_frate(win, [background, rect, stim_image], frate=pm.frate, t=t_stim) # wait for the frame rate to be reached
    print(f"stimulus {i+1} presented in {time.time()-t1:.5f} seconds")
    background.draw()
    fix_cross.draw()
    win.flip()
    t3 = time.time()
    core.wait(t_isi)
    #fl.wait_frate(win, [background, fix_cross], frate=pm.frate, t=t_isi)
    print(f"stimulus {i+1} ISI in {time.time()-t3:.5f} seconds")
    return

def present_rewarded_sequences(tools:dict):
    ''' Tells the participant which sequences are rewarded for the last question.'''
    
    background = tools['background']
    win = tools['win']
    pport = tools['pport']
    logger = tools['logger']
    reward_seq = tools['reward_info']['reward']
    no_reward_seq = tools['reward_info']['no_reward']
    run_seq = reward_seq + no_reward_seq
    random.shuffle(run_seq) # shuffle the order of the sequences so the reawrded ones are not always first
    modality = 'img'
    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang=tools['exp_info']['lang'], seed=tools['seed'])

    first_stim_paths = {} # get the paths of the first images to be presented as indicators of each sequence
    for seq_name in run_seq:
        sequence = amodal_sequences[seq_name]
        first_stim = sm.get_stims(pm.input_dir, sequence, modality, lang=tools['exp_info']['lang'])[0] # only the first image
        first_stim_paths[seq_name] = first_stim

    # construct the grid to store the 6 images
    xs = [-0.5, 0, 0.5]*2
    y = .4
    ys = [y]*3 + [-y]*3

    # define the objects to be presented
    text = it.get_txt(tools['exp_info']['lang'], 'instr_reward_fn')
    instructions = visual.TextStim(
        win=win,
        text=text,
        pos=(0, 0.85),
        height=pm.text_height,
        color='black',
        units='norm'
    )
    stim_dict = {}
    for i, seq_name in enumerate(run_seq):
        hl_color = pm.rw_hl_color if seq_name in reward_seq else None # invisible highlight if no reward
        stim_dict[seq_name] = {}
        stim_dict[seq_name]['image'] = visual.ImageStim(
            win=win,
            image=first_stim_paths[seq_name],
            pos=(xs[i], ys[i]),
            size=(pm.rw_img_size, pm.rw_img_size * tools['aspect_ratio']),
        )
        stim_dict[seq_name]['highlight'] = visual.Rect(
            win=win,
            width=pm.rw_hl_size,
            height=pm.rw_hl_size * tools['aspect_ratio'],
            pos=(xs[i], ys[i]),
            fillColor=hl_color,
        )

    logger.info('Presenting rewarded sequences')
    logger.info(f'rewarded sequences: {reward_seq}')

    # display images for 1 s before the highligh
    background.draw()
    instructions.draw()
    for seq_name in stim_dict:
        stim_dict[seq_name]['image'].draw()
    win.flip()
    core.wait(1)

    # start the flickering loop 
    start_time = time.time()
    t_stop = start_time + pm.t_reward_info
    i_count = 0

    while time.time() < t_stop:
        elapsed_time = time.time() - start_time
        flick_val = 0.5 * (1 + math.sin(2 * math.pi * pm.flick_freq * elapsed_time)) # smooth flicker 
        background.draw()
        instructions.draw()
        for seq_name in stim_dict:
            highlight = stim_dict[seq_name]['highlight']
            highlight.opacity = flick_val
            highlight.draw()
            stim_dict[seq_name]['image'].draw()
        if i_count == 0:
            win.callOnFlip(pport.signal, pm.triggers['misc']['reward_info']) # send trigger at the beginning of the reward pres
        win.flip()
        i_count += 1

    logger.info('Rewarded sequences presented successfully')
    return 


#########################
# highest level functions

def pipeline(debugging=False):
    tools = execute_run(debugging=debugging)
    post_run_break(tools, pause_i=1)
    present_rewarded_sequences(tools)
    post_run_break(tools, pause_i=2)
    bonus_question(tools)
    # if tools['exp_info']['run'] == '02':
    #     play_tmr(tools)
    fl.end_expe(tools)

def test_pipeline(debugging=True):
    tools = execute_run(debugging)
    tools['win'].close()

if __name__ == '__main__':
    pipeline(debugging=True)
