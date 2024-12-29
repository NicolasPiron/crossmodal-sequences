from psychopy import visual, event, core
import glob
import os
import src.params as pm
import src.flow as fl
import src.stimuli_manager as sm

# This scripts shows the images and the related words to the participant

def present_stims():

    # get all the stimuli
    all_items = glob.glob("data/input/stims/*/*.png")
    all_items = sorted(set([os.path.basename(item).split('_')[0] for item in all_items]))   
    all_img = sorted(glob.glob("data/input/stims/*/*img.png"))
    all_txt = sorted(glob.glob("data/input/stims/*/*txt.png"))

    # Create a window
    win = visual.Window(size=pm.win_size,
                        fullscr=True,
                        color=(255, 255, 255),
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

    with open(pm.instr_stimpres_fn, "r", encoding="utf-8") as file:
        instructions_text = file.read()

    fl.type_text(instructions_text,
                win,
                height=pm.text_height,
                background=background,
                t=pm.t)

    event.waitKeys(keyList=['space'])

    for item in all_items: # match the image and the text
        item_img = [img for img in all_img if item in img][0]
        item_txt = [txt for txt in all_txt if item in txt][0]

        win.flip()
        core.wait(0.01) # to add a white flash between stims
        fl.check_escape(win)

        img_stim = visual.ImageStim(
            win, 
            image=item_img,
            size=(pm.img_size, pm.img_size*aspect_ratio),
            pos=(0, 0.3),
            units="norm"
        )

        txt_stim = visual.ImageStim(
            win, 
            image=item_txt,
            size=(pm.img_size, pm.img_size*aspect_ratio),
            pos=(0, -0.3),
            units="norm"
        )

        txt_instr = visual.TextStim(
            win, text="Appuyez sur ESPACE pour passer à l'item suivant",
            font="Arial",
            color='black',
            height=pm.text_height,
            pos = (0, -0.8),
            alignText="center" )

        #background.draw()
        img_stim.draw()
        txt_stim.draw()
        txt_instr.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

    # Tell the participant that the presentation is over, and to call the experimenter
    fl.type_text("La présentation est terminée, l'expérience peut commencer. Veuillez attendre l'expérimentateur.",
                win,
                height=pm.text_height,
                background=background,
                t=pm.t)

    event.waitKeys(keyList=['space'])
    win.close()

if __name__ == "__main__":
    sm.check_img_txt(pm.input_dir) 
    present_stims()