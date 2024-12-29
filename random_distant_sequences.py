import random

# Generate random order, with minimal overlap between sequences

# Original sequences
seq_structures = {
    'A': [0, 1, 2, 3, 4, 5],
    'B': [3, 1, 4, 0, 5, 2],
    'C': [5, 3, 2, 0, 4, 1],
    'D': [2, 4, 1, 5, 0, 3],
    'E': [4, 5, 0, 3, 1, 2],
    'F': [1, 0, 5, 2, 3, 4],
}

def calculate_pairwise_differences(seq_structures):
    keys = list(seq_structures.keys())
    n = len(keys)
    differences = {key: 0 for key in keys}
    for i in range(n):
        for j in range(i + 1, n):
            diff = sum(1 for x, y in zip(seq_structures[keys[i]], seq_structures[keys[j]]) if x != y)
            differences[keys[i]] += diff
            differences[keys[j]] += diff
    return differences

# Shuffle and calculate differences
best_score = 0
best_sequences = None

for _ in range(1000):  # Attempt 1000 different shuffles
    new_sequences = {k: random.sample(v, len(v)) for k, v in seq_structures.items()}
    differences = calculate_pairwise_differences(new_sequences)
    total_difference = sum(differences.values())
    if total_difference > best_score:
        best_score = total_difference
        best_sequences = new_sequences

print(best_sequences)
print(best_score)
