import pandas as pd

def convert(file):
    read_file = pd.read_excel(file)
    read_file.to_csv('converted.csv', index = None, header=True)
    return