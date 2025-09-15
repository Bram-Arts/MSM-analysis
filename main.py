import filereader
import breeder
import pandas as pd

df = filereader.read_data()
breeder.add_possible_results_to_df(df)
df["Possible results"].to_excel("possible_results.xlsx")
# df["Possible results"].to_csv("possible_results.csv")