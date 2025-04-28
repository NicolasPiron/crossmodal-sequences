from psychopy import visual, event, core
from psychopy.hardware.keyboard import Keyboard
from pathlib import Path
import random
import platform
import glob
import os
import pandas as pd
import sequences.params as pm
import sequences.bonus_q as bq
import sequences.stimuli_manager as sm
import sequences.instr as it
from sequences.common import get_win_dict

def ask_sequence(start_item, seq_name, amodal_sequences, tools):
    '''Ask the participant to place the images in the correct order and save the data.
    
    Parameters
    ----------
    start_item : str
        The starting item of the sequence
    seq_name : str
        The name of the sequence
    amodal_sequences : dict
        A dictionary containing the sequences that are in the run {'A': [item1, item2, ...], ...}
    tools : dict
        A dictionary containing the tools needed for the experiment. It contains:
            - exp_info: a dictionary containing the experiment information
            - win: the window object
            - background: the background object
            - logger: the logger object
        
    Returns
    -------
    '''

    subject_id = tools['exp_info']['ID']
    run_id = tools['exp_info']['run']
    lang = tools['exp_info']['lang']
    win = tools['win']
    background = tools['background']
    aspect_ratio = tools['aspect_ratio']
    logger = tools['logger']

    out_dir = Path(f"{pm.output_dir}/sub-{subject_id}/bonus")
    os.makedirs(out_dir, exist_ok=True)
    out_path = Path(f"{out_dir}/sub-{subject_id}_run{run_id}_bonus_{seq_name}.csv")

    txt_instr2 = it.get_txt(lang, 'instr_bonus2_fn')
    instr2 = visual.TextStim(win, text=txt_instr2, pos=(0, 0.7), color="black")
    # filter out the images that are not in the run
    # 1) extract the items from the sequences
    amodal_items = []
    for seq in amodal_sequences.values():
        for item in seq:
            amodal_items.append(item)
    # 2) get the paths of the images that are in the run
    img_files = glob.glob(str(pm.input_dir) + f"/stims/{lang}/*/*img.png")
    img_files = [img for img in img_files if Path(img).stem.split('_')[0] in amodal_items]
    random.shuffle(img_files)
    start_item_path = glob.glob(str(pm.input_dir) + f"/stims/{lang}/*/{start_item}_img.png")[0]
    
    start_item_index = img_files.index(start_item_path) # needed to fill the removed item's position with the dummy image
    img_files.remove(start_item_path)
    dummy_path = None
    img_files.insert(start_item_index, dummy_path)

    positions = bq.gen_img_positions(jitter=0.05)

    start_item_img = visual.ImageStim(
        win,
        image=start_item_path,
        pos=(-0.75, 0.4),
        size=(pm.bq_img_size, pm.bq_img_size * aspect_ratio),
    )

    # define dictionaries for images and slots. This will allow us to keep track of what happens to them.
    images = []
    for i, img_path in enumerate(img_files):
        # this dummy image is used to fill the blank left by the cue
        if img_path is None: 
            # create an invisible placeholder
            img_stim = visual.ImageStim(win, image=None, opacity=0, pos=positions[i])
            images.append({
                "stim": img_stim,
                "highlight": visual.Rect(win, opacity=0),  # never shown
                "orig_pos": positions[i],
                "selected": False,
                "placed": True,  # prevent interaction
                "current_slot": None,
            })
            continue
        img_stim = visual.ImageStim(
            win,
            image=img_path,
            pos=positions[i],
            size=(pm.bq_img_size, pm.bq_img_size * aspect_ratio),
        )
        highlight = visual.Rect(
            win,
            width=pm.bq_hl_size,
            height=pm.bq_hl_size * aspect_ratio,
            pos=positions[i],
            lineColor="blue",
            lineWidth=5,
            opacity=0,
        )
        images.append(
            {
                "stim": img_stim,
                "highlight": highlight,
                "orig_pos": positions[i],
                "selected": False,
                "placed": False,
                "current_slot": None,
            }
        )

    slot_positions = [(-0.45, 0.4), (-0.15, 0.4), (0.15, 0.4), (0.45, 0.4), (0.75, 0.4)]
    slots = [
        {
            "rect": visual.Rect(
                win,
                width=pm.bq_img_size,
                height=pm.bq_img_size * aspect_ratio,
                pos=pos,
                lineColor="black",
                fillColor=(105, 105, 105),
            ),
            "occupied": False,
            "image": None,
        }
        for pos in slot_positions
    ]

    grid_index = 0
    grid_cols = 6  # 6 columns as in gen_img_positions
    selected_image = None  # Track the currently selected image
    running = True
    direct_d = {pm.key_bq[key]:key for key in ['left', 'right', 'up', 'down']} # invert key values and subselect directions

    while running:
        background.draw()
        instr2.draw()
        start_item_img.draw()

        for i, img in enumerate(images):
            img["highlight"].opacity = 1 if i == grid_index and not img["placed"] else 0

        # Draw slots (only the empty ones)
        for slot in slots:
            if not slot["occupied"]:
                slot["rect"].draw()

        # Draw all images (whether placed or not)
        for img in images:
            img["stim"].draw()
            img["highlight"].draw()

        # Update the window
        win.flip()

        keys = event.getKeys()
        for key in keys:
            if key in list(direct_d.keys()): 
                grid_index = bq.move_cursor(grid_index, direct_d[key], len(images), grid_cols, images)
            elif key == pm.key_bq['confirm']:
                selected_image = bq.handle_select_or_place(images, grid_index, selected_image, slots)
            # elif key == pm.key_bq['remove']: # TODO: fix it
            #     bq.handle_undo(images)
        occ_count = bq.count_occupied_slots(slots)
        txt_instr3 = it.get_txt(lang, 'instr_bonus3_fn')
        # check if the participant has placed all images and if so, save the data
        running = bq.check_slot_filling(
            start_item_img, 
            images, 
            slots, 
            occ_count, 
            win, 
            background, 
            out_path, 
            txt_instr3,
            key_map=pm.key_bq,
            adapt_waitKeys=tools['adapt_waitKeys']
        )

        # if "escape" in event.getKeys():
        #     running = False
        
        core.wait(0.01) 
    
    if logger:
        logger.info(f"Bonus question: sequence {seq_name} completed")
    
    return

def ask_all_seq(tools:dict):
    '''Ask the participant to place the images in the correct order for all sequences in the run
    
    Parameters
    ----------
    tools : dict
        A dictionary containing the tools needed for the experiment. It contains:
            - exp_info: a dictionary containing the experiment information
            - win: the window object
            - background: the background object
            - logger: the logger object
        
    Returns
    -------
    None'''

    def shuffle_dict(d):
        items = list(d.items())
        random.shuffle(items)
        return dict(items)
    
    subject_id = tools['exp_info']['ID']
    run_id = tools['exp_info']['run']
    lang = tools['exp_info']['lang']
    win = tools['win']
    background = tools['background']
    logger = tools['logger']
    adapt_waitKeys = tools['adapt_waitKeys']
    #win.mouseVisible = False

    if logger:
        logger.info('=============== Beginning of bonus questions ===============')

    seed = sm.set_seed(subject_id)

    all_amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang, seed=seed)
    two_run_org = sm.generate_run_org(all_amodal_sequences, seed=seed)
    amodal_sequences = extract_sequences(two_run_org, run_id, all_amodal_sequences)
    amodal_sequences = shuffle_dict(amodal_sequences)

    background.draw()
    win.flip() 

    txt_instr1 = it.get_txt(lang, 'instr_bonus_fn')
    instructions = visual.TextStim(
        win, 
        text=txt_instr1, 
        pos=(0, 0), 
        color="black"
    )

    background.draw()
    instructions.draw()
    win.flip()
    adapt_waitKeys(keyList=pm.key_bq['confirm'])

    for seq in amodal_sequences:
        seq_name = seq[0]
        start_item = amodal_sequences[seq][0]
        ask_sequence(
            start_item, 
            seq_name=seq_name, 
            amodal_sequences=amodal_sequences,
            tools=tools,
        )
        
    if logger:
        logger.info("Bonus question: all sequences completed")
    return 

def extract_sequences(two_run_org, run_id, all_amodal_sequences):
    ''' Helper func to extract the sequences that are in the run.
    
    Parameters
    ----------
    two_run_org : dict
        The dictionary containing the sequences for each run. Format {'run1':{'block1':['A', 'B', 'C'], 'block2':['D', 'E', 'F']}, 'run2':...}
    run_id : str
        The run ID
    all_amodal_sequences : dict
        A dictionary containing all the sequences from A to L
        
    Returns
    -------
    dict
        A dictionary containing the sequences that are in the run {'A': [item1, item2, ...], ...} i.e. 6 sequences''' 

    run_seq = two_run_org['run'+str(int(run_id))]
    run_seq_names = []
    for val in run_seq.values(): # flatten the list of lists
        for i in val:
            run_seq_names.append(i)
    run_seq_names = set(run_seq_names)
    amodal_sequences = {k: v for k, v in all_amodal_sequences.items() if k in run_seq_names}
    return amodal_sequences

def cpt_reward_feedback(tools:dict):
    ''' Compute the amount due to the participant and save it in a file.
    
    Parameters
    ----------
    tools : dict
        A dictionary containing the tools needed for the experiment. It contains:
            - exp_info: a dictionary containing the experiment information
            - win: the window object
            - background: the background object
            - logger: the logger object
    '''

    logger = tools['logger']
    subject_id = tools['exp_info']['ID']
    run_id = tools['exp_info']['run']
    lang = tools['exp_info']['lang']
    # get the actual sequences that were used in the run
    n_rw_seq = int(pm.n_seq / 2)
    seed = sm.set_seed(subject_id)
    all_amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang, seed=seed)
    two_run_org = sm.generate_run_org(all_amodal_sequences, seed=seed)
    reward_info = sm.get_reward_info(two_run_org, seed, n=n_rw_seq)
    run_rw_info = reward_info['run'+str(int(run_id))]
    amodal_sequences = extract_sequences(two_run_org, run_id, all_amodal_sequences)
    seq_names = list(amodal_sequences.keys())
    
    answers = bq.get_all_answers(subject_id, run_id, seq_names)
    # create a dataframe with the correct answers
    corr_answers = pd.DataFrame()
    for seq_name, seq in amodal_sequences.items():
        cols = {'sequence':6*[seq_name], 'correct_answer':seq, 'slot':list(range(0, 6))}
        subdf = pd.DataFrame(cols)
        corr_answers = pd.concat([corr_answers, subdf], ignore_index=True)
    # merge the two dataframes on the sequence and slot columns
    answers = pd.merge(answers, corr_answers, on=['sequence', 'slot'], how='inner')
    # check if the answers are correct
    answers['correct'] = answers['correct_answer'] == answers['answer']
    answers['rewarded'] = answers['sequence'].isin(run_rw_info['reward']) # bool vals to indicate if the sequence was rewarded

    n_corr_total = answers['correct'].sum() - 6 # total number of correct answers
    # filter out the non-rewarded sequences and extrat the number of correct answers and compute the reward amount
    rew_answers = answers[answers['rewarded']] # only the rewarded sequences
    n_correct_rw = rew_answers['correct'].sum() - n_rw_seq # remove the 3 correct answers by default caused by the first item's presence
    reward_amount = n_correct_rw * pm.reward_value

    if logger:
        logger.info(f"Bonus question: {n_corr_total} correct answers")
        logger.info(f"Bonus question: {n_correct_rw} rewarded answers")
        logger.info(f"Reward amount: {reward_amount} CHF")

    out_path = Path(f'{pm.output_dir}/sub-{subject_id}/sub-{subject_id}_run{run_id}_bonus.csv')
    answers.to_csv(out_path, index=False)
    if logger:
        logger.info("File with subject's performance saved")
    # save the reward amount in a file
    reward_file = Path(f'{pm.output_dir}/sub-{subject_id}/sub-{subject_id}_run{run_id}_bonus.txt')
    with open(reward_file, 'w') as f:
        f.write(f"Reward amount: {reward_amount} CHF\n")
        f.write(f"Rewarded sequences: {run_rw_info['reward']}\n")
        f.write(f"Number of correct answers: {n_corr_total}\n")
        f.write(f"Number of correct rewarded answers: {n_correct_rw}\n")

    if logger:
        logger.info("File with reward amount saved")

    return reward_amount, n_correct_rw

def display_rwd_amt(tools, reward_amount):
    ''' Display the reward amount and the number of correct answers.'''

    lang = tools['exp_info']['lang']
    win = tools['win']
    background = tools['background']
    logger = tools['logger']

    if reward_amount > 0:
        if lang == 'fr':
            txt = "Montant de la récompense: "
        else:
            txt = "Reward amount: "
        txt += f"{reward_amount} CHF\n!"
    else:
        if lang == 'fr':
            txt = "Vous n'avez pas gagné d'argent supplémentaire\n"
        else:
            txt = "You did not win any extra money\n"
    
    reward_text = visual.TextStim(
        win,
        text=txt,
        pos=(0, 0),
        color="black",
    )
    background.draw()
    reward_text.draw()
    win.flip()
    core.wait(5)

    if logger:
        logger.info("=============== End of bonus question ===============")

    return

def bonus_question(tools):
    ask_all_seq(tools)
    rwd, _ = cpt_reward_feedback(tools)
    display_rwd_amt(tools, rwd)

if __name__ == "__main__":

    if platform.system() == 'Linux':
        keyboard = Keyboard()
        keyboard.start()
        adapt_waitKeys = keyboard.waitKeys
    else:
        keyboard = None
        adapt_waitKeys = event.waitKeys

    subject_id = input('Enter subject ID: ')
    run_id = input('Enter run ID: ')
    win_dict = get_win_dict()
    tools = {
        'exp_info': {
            'ID': subject_id,
            'run': run_id,
            'lang': 'fr',
        },
        'win': win_dict['win'],
        'background': win_dict['background'],
        'aspect_ratio': win_dict['aspect_ratio'],
        'logger': None,
        'adapt_waitKeys':adapt_waitKeys,
    }
    ask_all_seq(tools) 
    rwd, n_corr = cpt_reward_feedback(tools)
    display_rwd_amt(tools, rwd)

