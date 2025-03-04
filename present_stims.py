from psychopy import visual, event, core
import glob
import os
import re
import sequences.params as pm
import sequences.flow as fl
import sequences.stimuli_manager as sm
import sequences.instr as it
from sequences.common import get_win_dict

# This scripts shows the images and the related words to the participant
def present_stims(lang="fr"):
    # get all the stimuli
    all_items = glob.glob(f"data/input/stims/{lang}/*/*.png")
    all_items = sorted(set([os.path.basename(item).split('_')[0] for item in all_items]))   
    all_img = sorted(glob.glob(f"data/input/stims/{lang}/*/*img.png"))
    all_txt = sorted(glob.glob(f"data/input/stims/{lang}/*/*txt.png"))

    # Create a window
    win_dict = get_win_dict()
    win = win_dict['win']
    background = win_dict['background']
    aspect_ratio = win_dict['aspect_ratio']
    win.mouseVisible = False

    instr1 = it.get_txt(lang, 'instr_stimpres_fn')
    fl.type_text(
        instr1,
        win,
        height=pm.text_height,
        background=background,
        t=pm.t,
    ) 

    event.waitKeys(keyList=['space'])

    for item in all_items: # match the image and the text
        
        # use regex with word boundaries to match exact words. # The \b ensures a word boundary (had an issue with 'ear' and 'bear')
        item_img_list = [img for img in all_img if re.search(rf'\b{item}_img\.png\b', img)] 
        item_txt_list = [txt for txt in all_txt if re.search(rf'\b{item}_txt\.png\b', txt)]

        if item_img_list and item_txt_list:
            item_img = item_img_list[0]
            item_txt = item_txt_list[0]
        else:
            print(f'Warning: No match found for {item}')

        win.flip()
        core.wait(0.02) # to add a white flash between stims
        fl.check_escape(win)

        img_stim = visual.ImageStim(
            win, 
            image=item_img,
            size=(pm.img_size, pm.img_size*aspect_ratio),
            pos=(0, 0.45),
            units="norm"
        )

        txt_stim = visual.ImageStim(
            win, 
            image=item_txt,
            size=(pm.img_size, pm.img_size*aspect_ratio),
            pos=(0, -0.25),
            units="norm"
        )

        instr2 = it.get_txt(lang, 'instr_stimpres2_fn')
        txt_instr = visual.TextStim(
            win,
            text=instr2,
            font="Arial",
            color='black',
            height=pm.text_height,
            pos = (0, -0.85),
            alignText="center"
        )

        #background.draw()
        img_stim.draw()
        txt_stim.draw()
        txt_instr.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

    # Tell the participant that the presentation is over, and to call the experimenter
    instr3 = it.get_txt(lang, 'instr_stimpres3_fn')
    fl.type_text(
        instr3,
        win,
        height=pm.text_height,
        background=background,
        t=pm.t
    )

    event.waitKeys(keyList=['space'])
    win.close()
    core.quit()

if __name__ == "__main__":
    lang = input("Langue (fr/en): ")
    sm.check_img_txt(pm.input_dir, lang) 
    present_stims(lang)