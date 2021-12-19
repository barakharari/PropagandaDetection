'''
Script for converting original election data csv into files that can
be passed into aschern model
'''

import pandas
import json
import re
import sys

from os.path import join, isdir
from os import mkdir
from util import remove_dir, create_fp_and_meta_files, check_files
from pathlib import Path

# Length of sequence of tokens being passed into model
SEQ_LENGTH = 75

# Write tweets into files that can be passed into aschern
def write_tweets(candidate, df, column, folder, file_type):

  # Create directory to store these results
  if not isdir(folder):
    mkdir(folder)

  # Loop through candidates DF and gather their tweets
  for i in range(df[column].shape[0]):
    tweets = json.loads(re.sub('\'', '\"',  df[column][i]))
    day = df["DATE"][i]
    category = column.lower()
    index = 1
    for tweet in tweets:
      article_name = candidate + "_" + category + "_" + str(i) + "_" + str(index) + "." + file_type
      index += 1
      with open(join(folder, article_name), "w") as f:

  # Write to txt file for aschern or write to json file
        if file_type == "txt":
          f.write(tweet["text"])
          f.write("\n\n")
        elif file_type == "json":
          tweet["date"] = day
          json.dump(tweet, f)

# Handle non tweets, which also need meta data
def write_non_tweets(candidate, df, non_tweet_folder, file_type, aschern=True):

  # Loop through the non tweets, check that directories exist and the such
  for i in range(df["NON_TWEETS"].shape[0]):
    if df["NON_TWEETS"][i] == []:
      continue
    category = df["CONTENT_CATEGORY"][i]
    if type(category) == float or not category or category == "tweet":
      continue
    folder = non_tweet_folder
    if not aschern:
      folder = join(non_tweet_folder, category)
    if not isdir(folder):
      mkdir(folder)

    # Construct article name and write to metadata / normal file with data to be 
    # passed into model. IMPORTANT TO NOTE that tokens are considered as characters
    # not full words!
    article_name = candidate + "_" + category + "_" + str(i) + "." + file_type
    fp_file_path = join(folder, article_name)
    if file_type == "txt":
      # Get meta file name and create
      meta_file_name = candidate + "_" + "_".join(category.split()) + "_" + str(i) + ".csv"
      meta_file_folder = join(non_tweet_folder, "meta")
      meta_file_path = join(meta_file_folder, meta_file_name)
      Path(meta_file_folder).mkdir(parents=True, exist_ok=True)

      text = df["NON_TWEETS"][i]  
      sentences = re.split('\.\s', text)
      index, token_spans, tokens = 0, [], []
      for sentence in sentences:
        s = sentence.split()
        token_spans.append((index, index+len(s)))
        tokens.extend(s)
        index += len(s)
      
      create_fp_and_meta_files(sentences, token_spans, tokens, meta_file_path, fp_file_path, SEQ_LENGTH)

    elif file_type == "json":
      with open(fp_file_path, "w") as f:
        data = {"text": df["NON_TWEETS"][i], "date": df["DATE"][i]}
        json.dump(data, f)

if __name__ == "__main__":

  # Load dataframes from csvs
  trump_df_name = "../data/DT_data.csv"
  hillary_df_name = "../data/HC_data.csv"
  base_folder = "aschern_data"

  # Assert that we pass in the right args
  assert len(sys.argv) >= 2, "Not enough args...\n\tpython election_data_to_aschern.py [json | txt] [-o overwrite (optional)]\n"
  file_type = sys.argv[1]
  assert file_type == "json" or file_type == "txt", "Invalid file_type..."

  # Load DFs from csvs
  trump_df = pandas.read_csv(trump_df_name)
  hillary_df = pandas.read_csv(hillary_df_name)

  overwrite = len(sys.argv) == 3
  
  # Remove directories so we can write to them again
  if overwrite:
    remove_dir("meta")
    remove_dir("aschern_data")

  if file_type == "json":

    # Create new directories
    Path(join(base_folder, "donald_trump_campaign", "donald_trump")).mkdir(parents=True, exist_ok=True)
    Path(join(base_folder, "hillary_clinton_campaign", "hillary_clinton")).mkdir(parents=True, exist_ok=True)

    # Candidate, dataframe, column_name, folder_to_write_to, file_type
    write_tweets("HC", hillary_df, "TWEETS", join(base_folder, "hillary_clinton_campaign/hillary_clinton/tweets"), file_type)
    write_tweets("HC", hillary_df, "RETWEETS", join(base_folder, "hillary_clinton_campaign/hillary_clinton/retweets"), file_type)
    write_tweets("DT", trump_df, "TWEETS", join(base_folder, "donald_trump_campaign/donald_trump/tweets"), file_type)
    write_tweets("DT", trump_df, "RETWEETS", join(base_folder, "donald_trump_campaign/donald_trump/retweets"), file_type)

    # Candidate, dataframe, column_name, folder_to_write_to, file_type
    write_non_tweets("HC", hillary_df, join(base_folder, "hillary_clinton_campaign/hillary_clinton"), file_type)
    write_non_tweets("DT", trump_df, join(base_folder, "donald_trump_campaign/donald_trump"), file_type)

  elif file_type == "txt":

    if overwrite:

      # Create new directories
      Path(base_folder).mkdir(parents=True, exist_ok=True)

      # Candidate, dataframe, column_name, folder_to_write_to, file_type
      write_tweets("HC", hillary_df, "TWEETS", base_folder, file_type)
      write_tweets("HC", hillary_df, "RETWEETS", base_folder, file_type)
      write_tweets("DT", trump_df, "TWEETS", base_folder, file_type)
      write_tweets("DT", trump_df, "RETWEETS", base_folder, file_type)

      # Candidate, dataframe, column_name, folder_to_write_to, file_type
      write_non_tweets("HC", hillary_df, base_folder, file_type)
      write_non_tweets("DT", trump_df, base_folder, file_type)

    # Check files
    check_files(base_folder)    