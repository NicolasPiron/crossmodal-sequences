# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()

import sequences.stimuli_manager as sm
import sequences.params as pm
import pandas as pd

def extract_sequences(two_run_org, run_id, all_amodal_sequences):
    run_seq = two_run_org['run'+str(int(run_id))]
    run_seq_names = []
    for val in run_seq.values(): # flatten the list of lists
        for i in val:
            run_seq_names.append(i)
    run_seq_names = set(run_seq_names)
    amodal_sequences = {k: v for k, v in all_amodal_sequences.items() if k in run_seq_names}
    return amodal_sequences

subject_id = '01'
run_id = '01'
lang = 'fr'
seed = sm.set_seed(subject_id)
all_amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures, lang, seed=seed)
two_run_org = sm.generate_run_org(all_amodal_sequences, seed=seed)
amodal_sequences = extract_sequences(two_run_org, run_id, all_amodal_sequences)
seq_names = list(amodal_sequences.keys())
print(seq_names)

df = pd.DataFrame()
for seq_name, seq in amodal_sequences.items():
    cols = {
        'sequence':6*[seq_name],
        'correct_answer':seq,
    }
    subdf = pd.DataFrame(cols)
    df = pd.concat([df, subdf], ignore_index=True)

print(df)
 