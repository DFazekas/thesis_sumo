from runner import process_conflicts
import os


path = "C:/Users/thoma/OneDrive/Documents/Thesis/drafts/thesis_sumo/case_studies/case_study_01/scenario_01/output/data/"

for file in os.listdir(path):
    process_conflicts.main(
        inputFilePath=path + file,
        outputFilePath="./ssm.csv")
