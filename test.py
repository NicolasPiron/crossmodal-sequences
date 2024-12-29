
def play_run():

    run_id = 0 # let the user select the run id

    # 1. generate sequences (2 times because each sequence will be in two blocks)
    sequences = 2*[]

    # 2. iterate over blocks
    for block in range(4):
        print(f'-- Block {block + 1}')

        # chose 3 sequences
        seq = sequences[:3]
        # update sequences pool
        #sequences = sequences - seq
        # get the modality organization
        mod_order = range(6) # len 6
        # get the sequence order 
        seq_order = list() # len 6

        # 3. iterate over trials
        for i, modality in enumerate(mod_order):

            print(f'trial {i+1}')


def count_dupes(arr):
    '''Count the number of duplicates in a list'''

    seen = set()
    duplicate_counter = 0
    for item in arr:
        if item in seen:
            duplicate_counter += 1
        else:
            seen.add(item)
    return duplicate_counter

def sample_n_throw(arr, n=3):
    '''Sample n items from a list and remove them'''
    sample = random.sample(set(arr), n)
    for s in sample:
        arr.remove(s)
    return sample, arr

def sample_until_no_dupes(arr):
    '''Sample n items from a list and remove them'''
    temp = arr.copy()
    sample, new_temp = sample_n_throw(temp, 3)
    if count_dupes(new_temp) > 0:
        duplicate = True
        while duplicate:
            temp = arr.copy()
            sample, new_temp = sample_n_throw(temp, 3)
            if count_dupes(new_temp) == 0:
                duplicate = False
    return sample, new_temp

import random

mega_dupe_counter = []
for j in range(10):

    vals = ['A', 'B', 'C', 'A', 'D', 'C']

    for i in range(2):

        if i == 0:
            print('iteration 1')
            sample, new_vals = sample_until_no_dupes(vals)
            vals = new_vals
                
        else:
            print('iteration 2')
            sample = random.sample(set(vals), 3)
            for s in sample:
                vals.remove(s)
        print(f'sample: {sample}')

    print(f'iteration {j+1} done')



# mega_dupe_counter = []

# for j in range(10000):
    
#     # Define the unique sequences (e.g., unique items for drawing)
#     unique_sequences = ['A', 'B', 'C', 'D', 'E', 'F']
#     unique_sequences_pool = unique_sequences * 2  # Two copies of each unique sequence
#     print("Initial unique_sequences_pool:", unique_sequences_pool)

#     duplicate_counter = 0
#     # Iterate 4 times to draw 3 unique items per iteration
#     for i in range(4):  # 4 iterations to draw all items
#         trial = i + 1  # Define trial number
        
#         # Randomly sample 3 unique items from the current pool of unique_sequences
#         chosen_sequences = random.sample(set(unique_sequences_pool), 3)

#         if i == 2:
#             print(f"Remaining unique_sequences_pool: {unique_sequences_pool}")
#             # count duplicates
#             seen = set()
#             for item in unique_sequences_pool:
#                 if item in seen:
#                     duplicate_counter += 1
#                 else:
#                     seen.add(item)
#             mega_dupe_counter.append(duplicate_counter)
#             break

#         # Remove the chosen items from the pool
#         for item in chosen_sequences:
#             unique_sequences_pool.remove(item)
        
#         # # Debug prints for clarity
#         # print(f"Iteration {trial}: Chosen sequences = {chosen_sequences}")
#         # print(f"Remaining unique_sequences_pool: {unique_sequences_pool}")

        
#     print(f'iteration {j+1} done')

# print(max(mega_dupe_counter))
# if __name__ == '__main__':

#     #present_stims()
#     play_run()
#     play_run()


