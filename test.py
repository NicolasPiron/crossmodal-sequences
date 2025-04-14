# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()

import sequences.bonus_q as bq

x = bq.get_all_answers('00', '01', ['B', 'D', 'E', 'I', 'K', 'L'])
print(x)

# print(random.sample(['a', 'b', 'c', 'c'], 3))

# unique = set()±±
# for i in range(1000):
#     unique.add(random.randint(0, 10))
# print(unique)