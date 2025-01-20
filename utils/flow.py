from psychopy import visual, core, event
import warnings

def log_exceptions(message, logger, win):
    ''' Function to log exceptions and close the window '''
    warnings.warn('ERROR : exception occured, see log file for details')
    logger.error(message)
    logger.error("Traceback details:", exc_info=True)
    win.close()
    core.quit()

def check_escape(tools):
    ''' Function to check for the escape key '''
    keys = event.getKeys()
    if 'escape' in keys:
        print("--- Escape key pressed, exiting... ---")
        if tools['logger']:
            tools['logger'].info("Escape key pressed, exiting...")
        tools['win'].close()
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
        if background:
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

def check_demo_info(exp_info):
    '''Check if user has entered all the necessary information for the demo'''

    if len(exp_info.get('ID', '')) == 0:
        print("--- No participant ID entered, exiting... ---")
        quit()
    elif len(exp_info.get('run', '')) == 0:
        print("--- No run number entered, exiting... ---")
        quit()

    sequences = exp_info.get('sequences', '')
    if len(sequences) != 3 or not all(char in 'ABCDEF' for char in sequences):
        print("--- Invalid 'sequences': Must be length 3 and contain only 'ABCDEF'. Exiting... ---")
        quit()

    nseq = exp_info.get('nseq')
    if not isinstance(nseq, int) or not (1 <= nseq <= 6):
        print("--- Invalid 'nseq': Must be an integer between 1 and 6. Exiting... ---")
        quit()

    order = exp_info.get('order', '')
    if order not in ('fixed', 'random'):
        print("--- Invalid 'order': Must be 'fixed' or 'random'. Exiting... ---")
        quit()

    start_modality = exp_info.get('start modality', '')
    if start_modality not in ('txt', 'img'):
        print("--- Invalid 'start modality': Must be 'txt' or 'img'. Exiting... ---")
        quit()

    only_questions = exp_info.get('only questions', '')
    if only_questions not in ('yes', 'no'):
        print("--- Invalid 'only questions': Must be 'yes' or 'no'. Exiting... ---")
        quit()
        
    print("--- Valid info entered, ready to proceed ---")

def handle_user_cancel(dlg, logger=None):
    '''Handle user cancellation gracefully'''
    if not dlg.OK:
        warnings.warn('WARNING : User cancelled the experiment')
        core.quit()