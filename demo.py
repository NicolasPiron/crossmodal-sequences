# create a demo for the participants to understand the task. 
from sequences.common import get_win_dict
from sequences import params as pm
from sequences import flow as fl
from sequences import stimuli_manager as sm
from sequences import instr as it
from psychopy import visual, core, event
from psychopy.gui import DlgFromDict
import glob
import os

def init_run():
    exp_info = {
        'lang': 'fr'
    }
    dlg = DlgFromDict(exp_info, title='Enter language for demo', sortKeys=False)
    fl.handle_user_cancel(dlg)
    fl.check_demo_info(exp_info)

    win_dict = get_win_dict()
    win_dict['win'].mouseVisible = False

    tools = {
    'demo': True,
    'debugging': None,
    'logger': None,
    'win': win_dict['win'],
    'aspect_ratio': win_dict['aspect_ratio'],
    'background': win_dict['background'],
    'wait_fun': core.wait,
    'event_fun': event.getKeys,
    'clear_event_fun':event.clearEvents,
    'exp_info': exp_info,
    }

    return tools

def present_seq(items, tools):
    for i in items:
        present_stimulus(tools, i)
    return None

def present_stimulus(tools, stim):
    ''' Present a single stimulus. Returns nothing. '''
    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    t_stim = pm.stim_dur + sm.jitter_isi(pm.jitter)
    t_isi = pm.isi_dur

    tools = {"logger": None} # No logger for the demo
    fl.check_escape(tools)
    stim_image = visual.ImageStim(
        win=win,
        image=stim,
        size=(pm.img_size, pm.img_size*aspect_ratio)
    )
                                                    
    background.draw()
    stim_image.draw()
    win.flip()
    core.wait(t_stim)

    # Display fixation cross
    fix_cross = visual.TextStim(
        win=win,
        text='+',
        font='Arial',
        height=0.1,
        color='black',
        units='norm',
    )
    background.draw()
    fix_cross.draw()
    win.flip()
    core.wait(t_isi)
    return None

def prep_question(tools):

    t_prep = pm.t_prep
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

def ask_trial_question(stims, tools):
    win = tools['win']
    aspect_ratio = tools['aspect_ratio']
    background = tools['background']
    exp_info = tools['exp_info']
    idx1, idx2 = sm.draw_two(ignore_idx=None) # draw two items from the sequence (e.g. (0, 4))                        
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

    background.draw()
    cue_viz.draw()
    win.flip()
    sm.fade_out(tools, cue_viz, clock=fade_clock, f_dur=t_viz_cue)

    background.draw()
    target_viz.draw()
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
    feedback_txt, font_color, _, _ = sm.get_feedback_args(distance, lang=exp_info['lang'])

    feedback = visual.TextStim(win=win,
        text=feedback_txt,
        pos=(0, 0),
        font="Arial",
        color=font_color, 
        height=pm.text_height,
        units='norm',
        bold=True
    )
    
    background.draw()
    feedback.draw()
    win.flip()
    core.wait(t_fb)

    return None

def main():
    tools = init_run()
    stims = sorted(glob.glob(os.path.join(pm.input_dir, 'stims', 'demo', '*.png')))
    print(stims)
    present_seq(stims, tools)
    prep_question(tools)
    ask_trial_question(stims, tools)
    tools['win'].close()

if __name__ == '__main__':
    main()