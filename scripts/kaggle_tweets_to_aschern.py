import sys
import pandas
from os.path import join, isdir
from os import mkdir
from pathlib import Path
from util import remove_dir, create_fp_and_meta_files, check_files

# Split up tweets so that model can process them all (and in parallel)
NUM_TWEETS_PER_FILE = 500

def write_kaggle_tweets(candidate, df, column, folder):
  # Make tweets dir if doesn't exist
  if not isdir(folder):
    mkdir(folder)

  # Loop through the dataframe, write every 500 tweets to a new file
  index = 0
  while (index < df.shape[0]):

    fp_file_path = join(folder, candidate + str(index) + "_" + str(index+NUM_TWEETS_PER_FILE) + ".txt")
    meta_file_folder = join(folder, "meta")
    Path(meta_file_folder).mkdir(parents=True, exist_ok=True)
    meta_file_path = join(meta_file_folder, candidate + str(index) + "_" + str(index+NUM_TWEETS_PER_FILE) + ".csv")

    sentences, spans = [], []
    start_index = 0
    for i in range(index, min(index+NUM_TWEETS_PER_FILE, df.shape[0])):
      tweet = df[column][i].replace("\n", " ")
      tweet = " ".join(tweet.split())
      sentences.append(tweet)
      spans.append((start_index, start_index + len(tweet)))
      start_index += len(tweet) + 1
    
    create_fp_and_meta_files(meta_file_path, fp_file_path, sentences, spans)

    index+=NUM_TWEETS_PER_FILE

trump_hillary_tweets_name = "../data/hillary_trump_tweets.csv"
base_folder = "kaggle_data"

trump_hillary_tweets_df = pandas.read_csv(trump_hillary_tweets_name)

trump_df = trump_hillary_tweets_df.loc[trump_hillary_tweets_df["handle"] == "realDonaldTrump"].reset_index()
hillary_df = trump_hillary_tweets_df.loc[trump_hillary_tweets_df["handle"] == "HillaryClinton"].reset_index()

# Assert that we pass in the right args
# print("Usage: python kaggle_tweets_to_aschern.py [-o overwrite (optional)]\n")

overwrite = len(sys.argv) == 2
if overwrite:
  
  remove_dir(base_folder)
  Path(base_folder).mkdir(parents=True, exist_ok=True)

  write_kaggle_tweets("DT", trump_df, "text", base_folder)
  write_kaggle_tweets("HC", hillary_df, "text", base_folder)

# Check files
check_files(base_folder)