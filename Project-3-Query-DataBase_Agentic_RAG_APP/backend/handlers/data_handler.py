import os
import pandas as pd

class DataHandler:
    def __init__(self):
        self.dataframes = {}

    def load_csvs(self, files):
        for i, file in enumerate(files):
            df = pd.read_csv(file)
            self.dataframes[f"df{i+1}"] = df
        return list(self.dataframes.keys())

    def get_dataframe(self, name):
        return self.dataframes.get(name, None)

    def get_all_data(self):
        return self.dataframes
