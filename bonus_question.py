from psychopy import visual, event, core
from pathlib import Path
import random
import glob
import sequences.params as pm
import sequences.bonus_q as bq
import sequences.stimuli_manager as sm
from sequences.common import get_win_dict

def ask_sequence(start_item, seq_name, subject_id, run_id, amodal_sequences, win_dict):
    '''Ask the participant to place the images in the correct order and save the data.
    
    Parameters
    ----------
    start_item : str
        The starting item of the sequence
    seq_name : str
        The name of the sequence
    subject_id : str
        The subject ID
    run_id : str
        The run ID
    amodal_sequences : dict
        A dictionary containing the sequences that are in the run {'A': [item1, item2, ...], ...}
    win_dict : dict
        A dictionary containing the window and background objects
        
    Returns
    -------
    win_dict : dict
        A dictionary containing the window and background objects'''

    out_path = Path(f"{pm.output_dir}/sub-{subject_id}/sub-{subject_id}_run{run_id}_bonus_{seq_name}.csv")

    win = win_dict['win']
    background = win_dict['background']
    aspect_ratio = win_dict['aspect_ratio']

    instr2 = visual.TextStim(
        win, text="De quels items est composée cette séquence?", pos=(0, 0.7), color="black"
    )
    # filter out the images that are not in the run
    # 1) extract the items from the sequences
    amodal_items = []
    for seq in amodal_sequences.values():
        for item in seq:
            amodal_items.append(item)
    # 2) get the paths of the images that are in the run
    img_files = glob.glob(str(pm.input_dir) + "/stims/*/*img.png")
    img_files = [img for img in img_files if Path(img).stem.split('_')[0] in amodal_items]
    random.shuffle(img_files)
    start_item_path = glob.glob(str(pm.input_dir) + f"/stims/*/{start_item}_img.png")[0]
    print(start_item_path)
    img_files.remove(start_item_path)
    positions = bq.gen_img_positions()

    start_item_img = visual.ImageStim(
        win,
        image=start_item_path,
        pos=(-0.75, 0.4),
        size=(pm.bq_img_size, pm.bq_img_size * aspect_ratio),
    )

    # define dictionaries for images and slots. This will allow us to keep track of what happens to them.
    images = []
    for i, img_path in enumerate(img_files):
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

    mouse = event.Mouse(win=win)
    selected_image = None  # Track the currently selected image
    running = True

    while running:
        background.draw()
        instr2.draw()
        start_item_img.draw()

        # Draw images and highlights
        for img in images:
            img["stim"].draw()
            img["highlight"].draw()
        for slot in slots:
            slot["rect"].draw()

        # Update the window
        win.flip()

        if mouse.getPressed()[0]:
            bq.undo_image_placement(images, mouse)
            selected_image = bq.toggle_image_selection(images, mouse, selected_image)
            bq.place_image_in_slot(slots, mouse, selected_image)

        occ_count = bq.count_occupied_slots(slots)
        running = bq.check_slot_filling(start_item_img, images, slots, occ_count, win, background, out_path)

        if "escape" in event.getKeys():
            running = False
    
    return win_dict

def ask_all_seq(subject_id, run_id, win_dict=None):
    '''Ask the participant to place the images in the correct order for all sequences in the run
    
    Parameters
    ----------
    subject_id : str
        The subject ID
    run_id : str
        The run ID
    win_dict : dict
        A dictionary containing the window and background objects
        
    Returns
    -------
    None'''

    def shuffle_dict(d):
        items = list(d.items())
        random.shuffle(items)
        return dict(items)
    
    if win_dict is None:
        win_dict = get_win_dict()

    win = win_dict['win']
    background = win_dict['background']
    win.mouseVisible = True

    out_dir = f"{pm.output_dir}/sub-{subject_id}"
    try:
        sm.r_and_set_seed(out_dir)
    except FileNotFoundError as e:
        print(e)

    two_run_org = sm.generate_run_org(pm.input_dir, pm.seq_structures)
    amodal_sequences = extract_sequences(two_run_org, run_id)
    amodal_sequences = shuffle_dict(amodal_sequences)

    background.draw()
    win.flip() 

    with open(pm.instr_bonus_fn, "r", encoding="utf-8") as file:
        txt = file.read()

    instructions = visual.TextStim(
        win, 
        text=txt, 
        pos=(0, 0), 
        color="black"
    )

    background.draw()
    instructions.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    for seq in amodal_sequences:
        seq_name = seq[0]
        start_item = amodal_sequences[seq][0]
        print(f"Sequence: {seq_name}, start item: {start_item}")
        ask_sequence(
            start_item, 
            seq_name=seq_name, 
            subject_id=subject_id,
            run_id=run_id,
            amodal_sequences=amodal_sequences,
            win_dict=win_dict
        )
        
    win.close()
    print("All sequences completed")
    return None

def extract_sequences(two_run_org, run_id):
    ''' Helper func to extract the sequences that are in the run.
    
    Parameters
    ----------
    two_run_org : dict
        The dictionary containing the sequences for each run. Format {'run1':{'block1':['A', 'B', 'C'], 'block2':['D', 'E', 'F']}, 'run2':...}
    run_id : str
        The run ID
        
    Returns
    -------
    dict
        A dictionary containing the sequences that are in the run {'A': [item1, item2, ...], ...}'''

    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
    run_seq = two_run_org['run'+str(int(run_id))]
    run_seq_names = []
    for val in run_seq.values(): # flatten the list of lists
        for i in val:
            run_seq_names.append(i)
    run_seq_names = set(run_seq_names)
    amodal_sequences = {k: v for k, v in amodal_sequences.items() if k in run_seq_names}
    return amodal_sequences

if __name__ == "__main__":
    subject_id = input('Enter subject ID: ')
    run_id = input('Enter run ID: ')
    ask_all_seq(
        subject_id=subject_id, 
        run_id=run_id,
        win_dict=None, 
    )
    core.quit()

