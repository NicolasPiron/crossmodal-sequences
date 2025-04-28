# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()


d = {
'1':'a',
'2':'b',
}

d2 = {key:d[key] for key in ['1']}
print(d2)