# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()
# from psychopy import core, sound, event
# import sequences.stimuli_manager as sm
# import sequences.params as pm


# def play_tmr(tools):
#     ''' Play the targeted memory reactivation sounds. Returns nothing. '''
#     # pport = tools['pport']
#     # logger = tools['logger']
#     # win = tools['win']
#     # background = tools['background']

#     print(tools['sound_org'].keys())
#     sounds = [sound.Sound(fn) for fn in tools['sound_org'].values()]
#     for s in sounds:
#         s.play()
#         core.wait(1)

#     return



# amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang='fr', seed=42)

# sound_org = sm.distribute_snd(seq_names=list(amodal_sequences.keys()), snd_dir=pm.snd_stim_dir, seed=42) # get the sound organization for the sequences
# tools = {
#     'sound_org': sound_org,
#     }

# play_tmr(tools)

from sequences.common import get_win_dict

d = get_win_dict()

win = d['win']
bg = d['background']


for _ in range(120):
    win.flip()
print(win.getActualFrameRate())

