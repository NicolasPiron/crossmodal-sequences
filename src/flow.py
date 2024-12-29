from psychopy import visual, core, event
import warnings


def log_exceptions(message, logger, win):
    ''' Function to log exceptions and close the window '''

    warnings.warn(f'ERROR : exception occured, see log file for details')
    logger.error(message)
    logger.error("Traceback details:", exc_info=True)
    win.close()
    core.quit()

def check_escape(win, logger=None):
    ''' Function to check for the escape key '''

    keys = event.getKeys()
    if 'escape' in keys:
        print("--- Escape key pressed, exiting... ---")
        if logger:
            logger.info("Escape key pressed, exiting...")
        win.close()
        core.quit()

def type_text(text, win, color="black", height=0.08, background=None, t=0.03):
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
        core.wait(t)

def check_user_info(exp_info, logger=None):
    '''Check if user has entered all the necessary information'''

    # for now, the logger arg is useless because the filename cannot 
    # be set before participant info is entered
    if len(exp_info['ID']) == 0:
        print("--- No participant ID entered, exiting... ---")
        if logger:
            logger.error("No participant ID entered, exiting...")
        quit()
    elif len(exp_info['run']) == 0:
        print("--- No run number entered, exiting... ---")
        if logger:
            logger.error("No run number entered, exiting...")
        quit()
    else:
        print("--- Participant info entered ---")
        if logger:
            logger.info("Participant info entered")

def handle_user_cancel(dlg, logger=None):
    '''Handle user cancellation gracefully'''

    if not dlg.OK:
        warnings.warn('WARNING : User cancelled the experiment')
        core.quit()