from psychopy import visual, core
from stimuli.audio import Sound
from sequences.common import get_win_dict
import time
import matplotlib.pyplot as plt


win_d = get_win_dict()
win = win_d["win"]
bg = win_d["background"]
vis_stim = visual.ImageStim(
    win=win,
    image='data/input/stims/en/bodyparts/arm_img.png',
    size=(0.5, 0.5 * win_d["aspect_ratio"]),
    units="norm",
    pos=(0, 0),
)
snd = Sound('data/input/sounds/seq_sounds/bass.wav')

rect = visual.Rect(
    win=win,
    width=0.5,
    height=0.5*win_d["aspect_ratio"],
    pos=(1, 1),
    units='norm',
    fillColor=(255, 255, 255),
)
    

def wait_frate(win, objects:list, frate:int, t:int):
    ''' Function to wait for a certain number of frames '''
    # Calculate the number of frames to wait
    frames = int(frate * t)
    # Wait for the specified number of frames
    for _ in range(frames):
        for obj in objects:
            obj.draw()
        win.flip()

frate = None

times = {}
clock = core.Clock()
for _ in range(20):
    bg.draw()
    rect.draw()
    vis_stim.draw()
    snd.play()
    win.callOnFlip(clock.reset)
    win.flip()
    #wait_frate(win, [bg, vis_stim], frate, 0.3)
    core.wait(0.3)
    t_stim = clock.getTime()
    print('stim time :', t_stim)
    times['stim'] = t_stim
    bg.draw()
    win.callOnFlip(clock.reset)
    win.flip()
    core.wait(1)
    #wait_frate(win, [bg, vis_stim], frate, 1)
    t_isi = clock.getTime()
    print('isi time :', t_isi)
    times['isi'] = t_isi

win.close()

fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].hist(times['stim'], bins=20)
ax[0].set_title('Stimulus Time')
ax[0].set_xlabel('Time (s)')
ax[0].set_ylabel('Frequency')
ax[1].hist(times['isi'], bins=20)
ax[1].set_title('ISI Time')
ax[1].set_xlabel('Time (s)')
ax[1].set_ylabel('Frequency')
plt.tight_layout()
plt.suptitle('Distribution of Stimulus and ISI Times')
plt.show()

