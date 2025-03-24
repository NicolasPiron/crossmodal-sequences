import pandas as pd
import glob
import os
import sequences.params as pm
from sequences.utils import extract_log_info, write_log_info_csv

def recover_position_info(csv_fn):
    ''' Recover the position information from the CSV file.'''
    df = pd.read_csv(csv_fn)
    run = int(df[df['Name'] == 'Run number'].iloc[-1:]['Value'].values[0])
    block = df[df['Name'] == 'block'].iloc[-1:]['Value'].values[0]
    trial = df[df['Name'] == 'trial'].iloc[-1:]['Value'].values[0]
    sequence = df[df['Name'] == 'sequence number'].iloc[-1:]['Value'].values[0]
    print(f'Run: {run}, Block: {block}, Trial: {trial}, Sequence: {sequence}')

    ## if question nr has a higher index (presented last) than the sequence nr, we are in the question phase

if __name__ == '__main__':
    subject_id = input('Enter the subject ID: ')
    run_id = input('Enter the run ID: ')
    subj_dir = os.path.join(pm.output_dir, f'sub-{subject_id}')
    log_fn = glob.glob(os.path.join(subj_dir, f'sub-{subject_id}_run-{run_id}*.log'))[0]
    log_info = extract_log_info(log_fn)
    out_fn = os.path.join(subj_dir, f'sub-{subject_id}_run-{run_id}_log.csv')
    write_log_info_csv(log_info, out_fn)
    print(f'Log entries written to {out_fn}')
    recover_position_info(out_fn)