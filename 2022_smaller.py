import pandas as pd


df_raw_file = pd.read_csv("2022.csv")

df_raw_file = df_raw_file[df_raw_file['FL_DATE'].str.startswith('2022-12-2')]

df_raw_file = df_raw_file[df_raw_file['AIRLINE_CODE'].isin(['WN', 'DL', 'AA', 'UA'])]

df_raw_file.to_csv("big_four_crisis_days.csv")


