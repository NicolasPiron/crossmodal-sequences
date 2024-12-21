from psychopy import visual, core, event
import warnings

def check_escape(win):
    ''' Function to check for the escape key '''

    keys = event.getKeys()
    if 'escape' in keys:
        print("--- Escape key pressed, exiting... ---")
        win.close()
        core.quit()

def type_text(text, win, color="black", height=0.08, background=None):
    ''' Function to display typing effect '''

    displayed_text = ""  # Start with an empty string
    for letter in text:
        displayed_text += letter
        text_stim = visual.TextStim(
            win, text=displayed_text, font="Arial", color=color, 
            height=height, alignText="center", wrapWidth=1.5, units="norm"
        )
        background.draw()
        text_stim.draw()
        win.flip()
        core.wait(0.03)

def check_user_info(exp_info):
    '''Check if user has entered all the necessary information'''

    if len(exp_info['ID']) == 0:
        print("--- No participant number entered, exiting... ---")
        quit()
    elif len(exp_info['run']) == 0:
        print("--- No run number entered, exiting... ---")
        quit()
    else:
        print("--- Participant info entered ---")

def handle_user_cancel(dlg):
    '''Handle user cancellation gracefully'''

    if not dlg.OK:
        warnings.warn('WARNING : User cancelled the experiment')
        core.quit()