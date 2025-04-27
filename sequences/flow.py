from psychopy import visual, core, event
import warnings


def end_expe(tools):
    win = tools['win']
    logger = tools['logger']
    logger.info(f"=============== Run {tools['exp_info']['run']} gracefully closed ===============")
    win.close()
    core.quit()

def novov_trigger(pport, trig1, trig2, delay=10):
    ''' Function to send triggers to the parallel port with no overlap.'''
    pport.signal(trig1)
    core.wait((delay+2)/1000)
    pport.signal(trig2)
    return

def clear_stuff(win):
    ''' Remove keyboard events and clear the window '''
    win.flip()
    core.wait(0.5)
    event.clearEvents()

def wait_frate(win, objects:list, frate:int, t:int):
    ''' Function to wait for a certain number of frames '''
    # Calculate the number of frames to wait
    frames = int(frate * t)
    # Wait for the specified number of frames
    for _ in range(frames):
        for obj in objects:
            obj.draw()
        win.flip()

def log_exceptions(message, logger, win):
    ''' Function to log exceptions and close the window '''
    warnings.warn('ERROR : exception occured, see log file for details')
    logger.error(message)
    logger.error("Traceback details:", exc_info=True)
    win.close()
    core.quit()

def check_escape_or_break(tools, pause_key='b'):
    ''' Function to check for the escape key or break key '''
    keys = event.getKeys()
    if 'escape' in keys:
        print("--- Escape key pressed, exiting... ---")
        if tools['logger']:
            tools['logger'].info("Escape key pressed, exiting...")
        tools['win'].close()
        core.quit()
    elif pause_key in keys:
        print(f"--- Break key pressed, pausing the experiment. Press {pause_key} to resume ---")
        if tools['logger']:
            tools['logger'].info("Break key pressed, pausing the experiment ...")
        tools['adapt_waitKeys'](keyList=[pause_key])
        if tools['logger']:
            tools['logger'].info("Break key pressed again, resuming the experiment ...")

    
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
    if exp_info['lang'] not in ('en', 'fr'):
        print("--- Invalid language entered, exiting... ---")
        quit()
    print("--- Valid info entered, ready to proceed ---")

def handle_user_cancel(dlg, logger=None):
    '''Handle user cancellation gracefully'''
    if not dlg.OK:
        warnings.warn('WARNING : User cancelled the experiment')
        core.quit()