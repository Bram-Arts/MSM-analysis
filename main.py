import filereader
import breeder
import pandas as pd
import slicer
import analysis

df = filereader.read_data()
# df = filereader.read_from_csv()
breeder.add_possible_results_to_df(df)
# df["Possible results"].to_excel("possible_results.xlsx")
# df["Possible results"].to_csv("possible_results.csv")

# print(slicer.look_for_outcome_group(df, ["Epic Yelmut", "Epic Edamimi"]))
target = "Epic Naturals singles"
subset = slicer.look_for_outcome_group(df, target)
subset = slicer.constant_torches(subset)
print(analysis.confidence_interval(subset, success = target))

print(subset)