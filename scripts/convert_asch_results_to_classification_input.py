import pandas
import sys
from os.path import join
import re

NUM_FINAL_RESULTS=13
PROP_TECHS = [
  "Loaded_Language",
  "Name_Calling,Labeling",
  "Repetition",
  "Exaggeration,Minimisation",
  "Doubt",
  "Appeal_to_fear-prejudice",
  "Flag-Waving",
  "Causal_Oversimplification",
  "Slogans",
  "Appeal_to_Authority",
  "Black-and-White_Fallacy",
  "Thought-terminating_Cliches",
  "Whataboutism,Straw_Men,Red_Herring",
  "Obfuscation,Intentional_Vagueness,Confusion",
  "Bandwagon,Reductio_ad_hitlerum"]
  

vector_df = pandas.DataFrame(columns=["File Name", "Candidate", "Sentence", "Propaganda Segments"] + PROP_TECHS)

assert len(sys.argv) >= 3, "Usage: python convert_asch_results_to_classification_input.py [path_to_results_folder] [path_to_data_folder] (-nm, optional arg no metadata)"
no_meta = len(sys.argv) == 4

results_folder = sys.argv[1]
data_folder = sys.argv[2]

# Loop through each result file
for i in range(NUM_FINAL_RESULTS):
  result_file = join(results_folder, str(i+1)+"_final_tc_results.txt")
  with open(result_file, "r") as rf:
    rf.readline()
    #Extract propaganda techniques and documents
    for line in rf:
      line = line.split()
      file_name = line[0]
      prop_start = line[1]
      prop_end = line[2]
      prop_line = " ".join(line[3:len(line)-1])
      prop_technique = line[len(line)-1]
      vector = [0]*14

      if no_meta:
        with open(join(data_folder, file_name), "r") as ff:
          tweet = ff.readline()
          if (vector_df["Sentence"] == tweet).any():
            vector_df.loc[vector_df["Sentence"] == tweet, "Propaganda Segments"] += ", \"" + prop_line + "\": " + prop_technique
            vector_df.loc[vector_df["Sentence"] == tweet, "Num Prop"] += 1
            vector_df.loc[vector_df["Sentence"] == tweet, prop_technique] += 1
          else:
            vector_df = vector_df.append(
              {"Candidate": file_name[0:2],
              "File Name": file_name, 
              "Sentence": tweet,
              "Propaganda Segments": prop_line + ": " + prop_technique,
              "Num Prop": 1,
              prop_technique: 1}, ignore_index=True)
      else:
        meta_file_path = join(data_folder, "meta",file_name.split(".")[0]+".csv")
        meta_df = pandas.read_csv(meta_file_path)

        for j in range(meta_df.shape[0]):
          sentence_info = meta_df.iloc[j]
          if int(sentence_info["start"]) <= int(prop_start) <= int(sentence_info["end"]):
            #Check if we've already found propaganda in this sentence
            if (vector_df["Sentence"] == sentence_info["sentence"]).any():
              vector_df.loc[vector_df["Sentence"] == sentence_info["sentence"],"Propaganda Segments"] += ", \"" + prop_line + "\": " + prop_technique
              vector_df.loc[vector_df["Sentence"] == sentence_info["sentence"],"Num Prop"] += 1
              vector_df.loc[vector_df["Sentence"] == sentence_info["sentence"],prop_technique] += 1
            else:
              vector_df = vector_df.append(
                {"Candidate": file_name[0:2],
                "File Name": file_name, 
                "Sentence": sentence_info["sentence"],
                "Propaganda Segments": prop_line + ": " + prop_technique,
                "Num Prop": 1,
                prop_technique: 1}, ignore_index=True)
            break
          elif int(sentence_info["start"]) > int(prop_start):
            break 
  print("Processed " + str(i+1), end="...")
vector_df.to_csv("classifier_training_data.csv")